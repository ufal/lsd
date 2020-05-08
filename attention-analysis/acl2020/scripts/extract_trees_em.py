import networkx as nx
from networkx.algorithms import tree
from tools import dependency, sentence_attentions

import argparse
from collections import defaultdict, namedtuple

import numpy as np
import json
import pandas as pd


RelData = namedtuple('RelData','layers heads d2p')
RelData2 = namedtuple('RelData', 'layers heads layersT headsT weight weightT')
RelData3 = namedtuple('RelData', 'layers heads weights d2p')

def rewrite_conllu(conllu_file, conllu_out_pred, conllu_out_gold,params_file, ann_file, break_after=1000, first_iter=True):
	
	CONLLU_ID = 0
	CONLLU_POS = 3
	CONLLU_LABEL = 7
	CONLLU_HEAD = 6
	
	new_params = dependency.conllu2pp_frame(None)
	#new_params = dependency.conllu2ll_frame(None)
	new_params += 0.01
	new_ann = []
	if not first_iter:
		with open(params_file, 'r') as infile:
			past_params = pd.DataFrame(json.load(infile))
		past_ann = np.load(ann_file)
		past_ann = [past_ann[f"arr_{i}"] for i in range(len(past_ann))]
	else:
		past_params = None
		past_ann = None
		
	reverse_label_map = {value: key for key, value in dependency.label_map.items()}
	reverse_label_map['object'] = 'obj'
	reverse_label_map['other'] = 'dep'
	
	lengths = []
	uas= []
	length_sent = 0
	out_lines = []
	out_lines_gold =[]
	
	dowrite = True
	pred = None
	gold = None
	ord2pos = None
	with open(conllu_file, 'r') as in_conllu:
		sentid = 0
		for line in in_conllu:
			if sentid > break_after:
				break
			if line == '\n':
				out_line = line.strip()
				out_line_gold = line.strip()
				if not sentid % 20:
					print(f"Processed sentence {sentid}", flush=True)
				if dowrite:
					uas_sent = (np.array(list(map(int, gold.ravel() != 'no edge'))) * np.array(
						list(map(int, pred.ravel() != 'no edge')))).sum() / np.array(list(map(int,gold.ravel()!='no edge'))).sum()
					uas.append(uas_sent)
					lengths.append(length_sent)
				sentid += 1
				
			elif line.startswith('#'):
				if line.startswith('# sent_id'):
					out_line = line.strip() + '/pred'
					out_line_gold = line.strip() + '/gold'
					pred, gold, ord2pos = multigraph_aborescene(sentid,first_iter, past_ann, new_ann, past_params, new_params)
					# pred, gold, node2lab = multigraph_aborescene(sentid, first_iter, past_ann, new_ann, past_params,
					#                                             new_params)
					dowrite = (pred is not None)
					length_sent = 0
				else:
					out_line_gold = line.strip()
					out_line = line.strip()
			else:
				fields = line.strip().split('\t')
				fields_gold = line.strip().split('\t')
				out_line_gold = line.strip()
				if fields[CONLLU_ID].isdigit() and pred is not None:
					length_sent += 1
					if fields[CONLLU_LABEL].strip() != 'root':
						col = pred.transpose()[int(fields[CONLLU_ID]) - 1]

						x = np.argwhere(col != 'no edge')
						x = x.item()
						lab = reverse_label_map[col[x][:-4]]
						lab_gold = reverse_label_map[dependency.transform_label(fields[CONLLU_LABEL])]
						
						fields[CONLLU_HEAD] = str(x + 1)
						fields[CONLLU_LABEL] = lab
						fields_gold[CONLLU_LABEL] = lab_gold

					fields[CONLLU_POS] = ord2pos[int(fields[CONLLU_ID]) - 1]
					#fields[CONLLU_POS] = dependency.transform_label2pos(node2lab[int(fields[CONLLU_ID]) - 1])
				out_line = '\t'.join(fields)
				out_line_gold = '\t'.join(fields_gold)		
			if dowrite:
				out_lines.append(out_line)
				out_lines_gold.append(out_line_gold)
	
	with open(conllu_out_pred, 'w') as out_conllu:
		out_conllu.write('\n'.join(out_lines))
		
	with open(conllu_out_gold, 'w') as out_conllu:
		out_conllu.write('\n'.join(out_lines_gold))

	np.savez(ann_file, *new_ann)
	
	with open(params_file, 'w') as out_params:
		json.dump(new_params.to_dict(), out_params)
		
	print("Estimaitions:")
	print(new_params)
	print("mena uas:")
	print(np.mean(np.array(uas)))
	print("length uas corr coef:")
	print(np.corrcoef(np.array(uas), np.array(lengths)))


def multigraph_aborescene(sentence_index, first_iter, past_ann, new_ann, past_params, new_params):
	matrices, sentence_id = next(attention_gen)
	if not matrices:
		return None, None, None

	assert sentence_index == sentence_id
	
	words_list = common_tokens[sentence_index]
	
	pos2ord = {pos: i for i, pos in enumerate(new_params.columns)}
	#lab2ord = {lab: i for i, lab in enumerate(new_params.columns)}
	if not first_iter:
		conditional_matrix = past_params.values / past_params.values.sum(axis=1, keepdims=True)
		x_prob = past_params.values.sum(axis=1, keepdims=True).transpose() / past_params.values.sum()
		if sentence_index == 0:
			print(x_prob)
	
	edge_labeled = {(h, d): l for d, h, l, p in dependency_rels[sentence_index] if l != 'root'}
	root_ord = 0
	for d, h, l, p in dependency_rels[sentence_index]:
		if l == 'root':
			root_ord = d
			break

	DG = nx.DiGraph()
	DG.add_edges_from(edge_labeled.keys())
	
	labels = {}
	for node in DG.nodes():
		labels[node] = words_list[node]
	
	MultiAttention = nx.MultiDiGraph()
	MultiAttention.add_nodes_from(DG.nodes())
	
	multi_edge2label = dict()
	for relation, rules in relation_rules.items():
		#aggr_matrix = np.average(np.array(matrices)[rules.layers, rules.heads, :, :],weights=rules.weights, axis=0)
		aggr_matrix = np.average(np.array(matrices)[rules.layers, rules.heads, :, :], axis=0)
		
		if consider_directions:
			if rules.d2p:
				aggr_matrix = aggr_matrix.transpose()
				
		aggr_matrix[:, root_ord] = 0.
		np.fill_diagonal(aggr_matrix, 0.)
		aggr_matrix = np.clip(aggr_matrix, 0.001, 0.999)
		
		if not consider_directions:
			aggr_matrixT = np.mean(np.array(matrices)[rules.layersT, rules.headsT, :, :], axis=0).transpose()
			aggr_matrixT[:, root_ord] = 0.
			np.fill_diagonal(aggr_matrixT, 0.)
			aggr_matrixT = np.clip(aggr_matrixT, 0.001, 0.999)
			weight = rules.weight ** 5
			weightT = rules.weightT ** 5
			aggr_matrix = (weight * np.log(aggr_matrix) + weightT * np.log(aggr_matrixT)) / (weight + weightT)
		else:
			aggr_matrix = np.log(aggr_matrix / (1 - aggr_matrix))

		
		if not first_iter:
			y_ord = pos2ord[dependency.transform_label2pos(relation[:-4])]
			#y_ord = lab2ord[relation[:-4]]
			#y_prob = (conditional_matrix[y_ord, np.newaxis] * x_prob).sum(axis=1, keepdims=True)
			y_prob = x_prob[:, y_ord]
			xy_prob = np.dot(conditional_matrix, past_ann[sentence_index])[y_ord, np.newaxis]
			prob_matrix = xy_prob / y_prob
			prob_matrix = np.log(prob_matrix.transpose())
			
			aggr_matrix = 1.0 * aggr_matrix + 1.0 * prob_matrix
			
		AG = nx.from_numpy_matrix(aggr_matrix, create_using=nx.DiGraph)
		
		for u, v, d in AG.edges(data=True):
			multi_edge2label[(u, v, d['weight'])] = relation
		# incldue statistical info about pos:
		
		MultiAttention.add_edges_from(AG.edges(data=True), label=relation)
	
	AttentionAborescene = tree.branchings.maximum_spanning_arborescence(MultiAttention)
	espanning = AttentionAborescene.edges(data=True)
	attention_labels = {(u, v): multi_edge2label[(u, v, d['weight'])] for u, v, d in espanning}


	# prepare output
	alabelm = np.full((len(aggr_matrix), len(aggr_matrix)), 'no edge', dtype='U24')
	dlabelm = np.full((len(aggr_matrix), len(aggr_matrix)), 'no edge', dtype='U24')
	
	parent2deps = defaultdict(list)
	node2pos = dict()
	node2pos[root_ord] = 'VERB'
	#node2lab = dict()
	#node2lab[root_ord] = 'root'
	for aedge, ael in attention_labels.items():

		alabelm[aedge[0], aedge[1]] = ael
		parent2deps[aedge[0]].append(aedge[1])
		node2pos[aedge[1]] = dependency.transform_label2pos(ael[:-4])
		#node2lab[aedge[1]] = ael[:-4]

	for dedge, deel in edge_labeled.items():
		
		deel = dependency.transform_label(deel)
		
		if deel + '-d2p' in relation_rules:
			dlabelm[dedge[0], dedge[1]] = deel + '-d2p'
		elif deel + '-p2d' in relation_rules:
			dlabelm[dedge[0], dedge[1]] = deel + '-p2d'
		
		elif 'other-d2p' in relation_rules:
			dlabelm[dedge[0], dedge[1]] = 'other-d2p'
		elif 'other-p2d' in relation_rules:
			dlabelm[dedge[1], dedge[0]] = 'other-p2d'
	
	#annotate POS-like tags
	prob_pos = np.zeros((len(new_params.columns), len(alabelm)))
	prob_pos[pos2ord['VERB'], root_ord] = 1.
	#prob_label = np.zeros((len(new_params.columns), len(alabelm)))
	#prob_label[lab2ord['root'], root_ord] = 1.
	curr_nodes = [root_ord]
	while curr_nodes:
		new_nodes = []
		for n in curr_nodes:
			for dep in parent2deps[n]:
				i = pos2ord[node2pos[dep]]
				prob_pos[i, dep] = 1
				new_params[node2pos[n]][node2pos[dep]] += 1
				#i = lab2ord[node2lab[dep]]
				#prob_label[i, dep] = 1.
				#new_params[node2lab[n]][node2lab[dep]] += 1
				
				new_nodes.append(dep)
		curr_nodes = new_nodes
	
	if not first_iter:
		prob_pos = (1. - DF)*prob_pos + DF*past_ann[sentence_index]
	new_ann.append(prob_pos)
	
	return alabelm, dlabelm, node2pos

	
if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-a", "--attentions", required=True, help="NPZ file with attentions")
	ap.add_argument("-t", "--tokens", required=True, help="Labels (tokens) separated by spaces")
	
	ap.add_argument("-c", "--conllu", help="Eval against the given conllu file")
	
	ap.add_argument("-o", "--output-pred")
	ap.add_argument("-g", "--output-gold")
	
	ap.add_argument("-m", "--maxlen", type=int, default=1000,
	                help="Skip sentences longer than this many words. A word split into several wordpieces is counted as one word. EOS is not counted.")
	
	ap.add_argument("-e", "--eos", action="store_true",
	                help="Attentions contain EOS")
	
	ap.add_argument("-n", "--no-softmax", action="store_true",
	                help="Whether not to use softmax for attention matrices, use with bert metrices")
	
	ap.add_argument("-f", "--first-iteration", action="store_true",
	                help="Whether it is the first iteration!")
	
	ap.add_argument("-s", "--seed", help="To identify temp fil	relation_rules = {relation: RelData2(**rules) for relation, rules in relation_rules.items()")
	
	ap.add_argument("-d", "--discarding", help="Factor responisble for discarding past annotations", type=float, default=0.)
	
	ap.add_argument("-j", "--json", type=str, help='json with head selcted.')
	
	ap.add_argument("-di", "--directional", action="store_true", help="whether to use direction averaging method.")
	
	args = ap.parse_args()
	
	global DF
	DF = args.discarding
	
	
	attentions_loaded = np.load(args.attentions)
	sentences_count = len(attentions_loaded.files)
	layers_count = attentions_loaded['arr_0'].shape[0]
	heads_count = attentions_loaded['arr_0'].shape[1]
	
	with open(args.tokens) as tokens_file:
		tokens_loaded = [l.split() for l in tokens_file]
	
	# in dependency_rels for each sentece there is a lists of tuples (token, token's head)
	# in dependency_rels_rev tuples are reversed.
	dependency_rels = dependency.read_conllu_labeled(args.conllu)
	
	grouped_tokens, common_tokens = dependency.group_wordpieces(tokens_loaded, args.conllu)
	
	attention_gen = sentence_attentions.generate_matrices(attentions_loaded, grouped_tokens, args.eos, args.no_softmax,
	                                                      args.maxlen, None)
	
	with open(args.json,'r') as json_in:
		relation_rules = json.load(json_in)
	
	considered_relations = ('adj-modifier', 'adv-modifier', 'auxiliary', 'compound', 'conjunct', 'determiner',
                'noun-modifier', 'num-modifier', 'object', 'other', 'subject', 'cc', 'case', 'mark')
	
	consider_directions = args.directional
	if consider_directions:
		relation_rules = {relation: RelData(**rules) for relation, rules in relation_rules.items()
		                  if relation[:-4] in considered_relations}
	else:
		relation_rules = {relation: RelData2(**rules) for relation, rules in relation_rules.items()
	                   if relation[:-4] in considered_relations}
	
	
	rewrite_conllu(args.conllu, args.output_pred, args.output_gold,
	               f'/lnet/tspec/tmp/limisiewicz/em_params-{args.seed}.json', f'/lnet/tspec/tmp/limisiewicz/em_annotations-{args.seed}.npz',
	               break_after=1000, first_iter=args.first_iteration)
