import networkx as nx
from networkx.algorithms import tree
from tools import dependency, sentence_attentions

import argparse
from collections import defaultdict, namedtuple

import numpy as np
import json
import pandas as pd


RelData = namedtuple('RelData','layers heads transpose d2p')
RelData2 = namedtuple('RelData', 'layers heads layersT headsT')
RelData3 = namedtuple('RelData', 'layers heads weights d2p')
#DF = 0.33

# soft pos mask (BEST)
# relation_rules  = {'adj-clause-p2d': RelData([3, 4, 7, 6, 5, 7], [3, 5, 6, 6, 9, 10],False, False),
#     'adj-modifier-d2p': RelData([3, 7, 4, 5], [9, 2, 5, 0],False, True),
#     'adv-clause-p2d': RelData([5, 3, 4, 5, 1], [8, 3, 8, 11, 5],False, False),
#     'adv-modifier-p2d': RelData([7, 5, 6, 4, 9, 4], [7, 1, 9, 7, 3, 10],False, True),
#     'apposition-p2d': RelData([3], [3],False, False),
#     'auxiliary-d2p': RelData([7, 3, 5, 4, 1, 1], [2, 9, 9, 11, 6, 1],False, True),
#     'clausal-p2d': RelData([5, 7, 7, 7, 4, 3, 5, 0, 6, 1], [8, 10, 1, 6, 5, 3, 11, 8, 6, 5],False, False),
#     'clausal-d2p': RelData([6, 5, 7, 7], [2, 3, 0, 9],False, True),
#     'compound-d2p': RelData([3, 7], [9, 2],False, True),
#     'conjunct-d2p': RelData([6, 9, 8, 4, 3, 11], [0, 6, 4, 10, 11, 9],False, True),
#     'determiner-d2p': RelData([7, 3, 4], [10, 9, 5],False, True),
#     # 'i object-d2p': RelData([5], [1],False, True),
#     'noun-modifier-d2p': RelData([6, 3, 7, 6], [9, 11, 9, 2],False, True),
#     'num-modifier-p2d': RelData([7, 4, 0, 6, 5], [11, 7, 2, 9, 9],False, False),
#     'object-d2p': RelData([6, 3, 6], [9, 11, 10],False, True),
#     'other-d2p': RelData([5, 4, 8, 6, 3, 5, 7, 7, 7, 5, 1, 1], [0, 5, 5, 6, 9, 7, 1, 2, 6, 9, 6, 1],False, True),
#     'punctuation-d2p': RelData([7, 8, 8, 5, 7, 8], [1, 5, 0, 7, 6, 4],False, True),
#     'subject-p2d': RelData([7, 4, 6], [4, 10, 4],False, False)}

# diagonal mask
# relation_rules = {'adj-clause-p2d': RelData([4, 7, 6, 0], [5, 6, 5, 8],False, False),
#     'adj-modifier-d2p': RelData([3, 7, 6, 5, 7, 8, 0, 2], [9, 10, 5, 7, 6, 5, 8, 11],False, True),
#     'adv-clause-d2p': RelData([4, 4, 5, 4, 2, 0], [9, 3, 4, 4, 7, 7],False, True),
#     'adv-modifier-d2p': RelData([7, 5, 6, 8, 7, 3, 10, 0, 6, 0], [6, 7, 5, 5, 10, 10, 10, 8, 4, 11],False, True),
#     'apposition-p2d': RelData([0, 9], [8, 0],False, False),
#     'auxiliary-d2p': RelData([3, 8, 7, 5, 4, 7, 10], [9, 5, 6, 0, 5, 10, 10],False, True),
#     'clausal subject-p2d': RelData([8, 0, 0, 0], [10, 8, 5, 1],False, False),
#     'clausal-d2p': RelData([7, 6, 4, 8, 5, 0, 0, 1, 0], [0, 2, 6, 8, 4, 5, 9, 11, 7],False, True),
#     'compound-d2p': RelData([3, 7, 6, 7, 0], [9, 6, 5, 10, 8],False, True),
#     'conjunct-d2p': RelData([4, 6, 4, 9, 5, 1, 0, 4, 6], [3, 0, 9, 6, 4, 10, 1, 4, 8],False, True),
#     'determiner-d2p': RelData([7, 3, 4, 8], [10, 9, 5, 10],False, True),
#     #'i object-d2p': RelData([6], [9],False, True),
#     'noun-modifier-p2d': RelData([4, 0, 9, 5, 3, 0, 0], [5, 8, 1, 8, 3, 1, 5],False, False),
#     'num-modifier-d2p': RelData([7, 6, 3, 8, 7, 6, 0, 10], [10, 5, 10, 5, 6, 4, 11, 10],False, True),
#     'object-d2p': RelData([7, 6, 4, 5, 3], [9, 9, 6, 3, 8],False, True),
#     'other-d2p': RelData([7, 4, 8, 6, 3, 0], [10, 5, 5, 5, 10, 8],False, True),
#     'punctuation-p2d': RelData([11, 10, 2, 11, 7, 7], [6, 7, 2, 2, 8, 7],False, False),
#     'subject-p2d': RelData([7, 4], [11, 10],False, False)}

# # diagonal mask2
# relation_rules  = {#'adj-clause-p2d': RelData([4, 7, 6, 0], [5, 6, 5, 8],False, False),
#     'adj-modifier-d2p': RelData([3, 7, 6, 5, 7, 8, 0, 2], [9, 10, 5, 7, 6, 5, 8, 11],False, True),
#     # 'adv-clause-p2d': RelData([4, 5, 5, 0, 4, 5, 11, 8, 3, 0], [3, 4, 5, 8, 9, 8, 8, 7, 1, 4],False, False),
#     'adv-modifier-d2p': RelData([7, 5, 6, 8, 7, 3, 10, 0, 6, 0], [6, 7, 5, 5, 10, 10, 10, 8, 4, 11],False, True),
#     # 'apposition-p2d': RelData([0, 9], [8, 0],False, False),
#     'auxiliary-d2p': RelData([3, 8, 7, 5, 4, 7, 10], [9, 5, 6, 0, 5, 10, 10],False, True),
#     'clausal subject-p2d': RelData([8, 0, 0, 0], [10, 8, 5, 1],False, False),
#     # 'clausal-p2d': RelData([5, 4, 7, 5, 0, 7, 4], [7, 5, 6, 8, 8, 1, 8],False, False),
#     'compound-d2p': RelData([3, 7, 6, 7, 0], [9, 6, 5, 10, 8],False, True),
#     # 'conjunct-d2p': RelData([4, 6, 4, 9, 5, 1, 0, 4, 6], [3, 0, 9, 6, 4, 10, 1, 4, 8],False, True),
#     'determiner-d2p': RelData([7, 3, 4, 8], [10, 9, 5, 10],False, True),
#     #'i object-d2p': RelData([6], [9],False, True),
#     'noun-modifier-p2d': RelData([4, 0, 9, 5, 3, 0, 0], [5, 8, 1, 8, 3, 1, 5],False, False),
#     'num-modifier-d2p': RelData([7, 6, 3, 8, 7, 6, 0, 10], [10, 5, 10, 5, 6, 4, 11, 10],False, True),
#     'object-d2p': RelData([7, 6, 4, 5, 3], [9, 9, 6, 3, 8],False, True),
#     'other-d2p': RelData([7, 4, 8, 6, 3, 0], [10, 5, 5, 5, 10, 8],False, True),
#     # 'punctuation-d2p': RelData([4, 8, 3, 7, 3], [5, 5, 10, 5, 9],False, True),
#     'subject-p2d': RelData([7, 4], [11, 10],False, False)
#     }

# up to 3 heads (diagonal masked):
# relation_rules = {#'adj-clause-p2d': RelData([4, 7, 6], [5, 6, 5],False, False),
# 	'adj-modifier-d2p': RelData([3, 7, 5], [9, 10, 7],False, True),
# 	# 'adv-clause-d2p': RelData([4, 4, 3], [9, 3, 1],False, True),
# 	'adv-modifier-d2p': RelData([7, 3, 6], [6, 10, 5],False, True),
# 	# 'apposition-p2d': RelData([0, 9], [8, 0],False, False),
# 	'auxiliary-d2p': RelData([3, 8, 4], [9, 5, 5],False, True),
# 	'clausal subject-p2d': RelData([8, 0, 0], [10, 8, 5],False, False),
# 	# 'clausal-d2p': RelData([7, 0, 5], [0, 5, 4],False, True),
# 	'compound-d2p': RelData([3, 7, 5], [9, 6, 7],False, True),
# 	'conjunct-d2p': RelData([4, 6, 0], [3, 0, 1],False, True),
# 	'determiner-d2p': RelData([7, 3, 4], [10, 9, 5],False, True),
# 	'noun-modifier-p2d': RelData([4, 0, 5], [5, 8, 8],False, False),
# 	'num-modifier-d2p': RelData([7, 6, 0], [10, 5, 8],False, True),
# 	'object-d2p': RelData([7, 6, 3], [9, 9, 8],False, True),
# 	'other-d2p': RelData([7, 4, 8], [10, 5, 5],False, True),
# 	# 'punctuation-p2d': RelData([11, 10, 7], [1, 2, 8],False, False),
# 	'subject-p2d': RelData([7, 4], [11, 10],False, False)
#     }


relation_rules2 = {
	'adj-modifier-d2p': RelData2([3, 5, 0], [5, 1, 2], [3, 7, 5], [9, 10, 7]),
	'adv-modifier-d2p': RelData2([4, 5, 8], [3, 4, 7],[7, 3, 6], [6, 10, 5]),
	'auxiliary-d2p': RelData2([7, 9, 7], [4, 2, 3],[3, 8, 4], [9, 5, 5]),
	'clausal subject-p2d': RelData2([8, 0, 0], [10, 8, 5],[9, 0, 2], [2, 0, 4]),
	'compound-d2p': RelData2([3, 7, 0], [5, 11, 2],[3, 7, 5], [9, 6, 7]),
	'conjunct-d2p': RelData2([5, 11, 0], [5, 8, 8],[4, 6, 0], [3, 0, 1]),
	'determiner-d2p': RelData2([5, 3, 8], [6, 2, 6],[7, 3, 4], [10, 9, 5]),
	'noun-modifier-p2d': RelData2([4, 0, 5], [5, 8, 8],[7, 0, 0], [9, 8, 7]),
	'num-modifier-d2p': RelData2([7, 9, 6], [11, 4, 2],[7, 6, 0], [10, 5, 8]),
	'object-d2p': RelData2([7, 4, 3], [10, 5, 9],[7, 6, 3], [9, 9, 8]),
	'other-d2p': RelData2([6, 8], [9, 6],[7, 4, 8], [10, 5, 5]),
	'subject-p2d': RelData2([7, 4], [11, 10],[5, 1, 7], [9, 6, 1])
    }

# relation_rules3 = {'adj-modifier-d2p': RelData3([3, 7, 5], [9, 10, 7],[1/3,1/4,1/2], True),
# 	'adv-modifier-d2p': RelData3([7, 3, 6], [6, 10, 5],[1/2,1,1/2], True),
# 	'auxiliary-d2p': RelData3([3, 8, 4], [9, 5, 5],[1/3,1/2,1/4], True),
# 	'clausal subject-p2d': RelData3([8, 0, 0], [10, 8, 5],[1,1/3,1], False),
# 	'compound-d2p': RelData3([3, 7, 5], [9, 6, 7],[1/3,1/2,1/2], True),
# 	'conjunct-d2p': RelData3([4, 6, 0], [3, 0, 1],[1,1,1], True),
# 	'determiner-d2p': RelData3([7, 3, 4], [10, 9, 5],[1/3,1/3,1/3], True),
# 	'noun-modifier-p2d': RelData3([4, 0, 5], [5, 8, 8],[1/3,1/2,1], False),
# 	'num-modifier-d2p': RelData3([7, 6, 0], [10, 5, 8],[1/4,1/2,1/3], True),
# 	'object-d2p': RelData3([7, 6, 3], [9, 9, 8],[1,1,1], True),
# 	'other-d2p': RelData3([7, 4, 8], [10, 5, 5],[1/4,1/4,1/2], True),
# 	'subject-p2d': RelData3([7, 4], [11, 10],[1,1], False)
#     }

# diagonal mask dpendent 2 parent only:
# relation_rules  = {'adj-clause-p2d': RelData([4, 7, 6, 0], [5, 6, 5, 8],False, False),
#     'adj-modifier-p2d': RelData([3, 6, 0, 4, 6, 7], [5, 11, 2, 7, 4, 4],False, False),
# 	'adv-clause-p2d': RelData([4, 5, 5, 0, 4, 5, 11, 8, 3, 0], [3, 4, 5, 8, 9, 8, 8, 7, 1, 4],False, False),
# 	'adv-modifier-p2d': RelData([7, 4, 0, 4, 9, 6, 8], [3, 7, 11, 6, 3, 2, 9],False, False),
#     'apposition-p2d': RelData([0, 9], [8, 0],False, False),
#     'auxiliary-p2d': RelData([7, 6, 5, 6, 7, 7, 5, 8, 9, 6, 2], [4, 3, 6, 9, 9, 3, 1, 11, 2, 2, 7],False, False),
#     'clausal subject-p2d': RelData([8, 0, 0, 0], [10, 8, 5, 1],False, False),
#     'clausal-p2d': RelData([5, 4, 7, 5, 0, 7, 4], [7, 5, 6, 8, 8, 1, 8],False, False),
#     'compound-p2d': RelData([3, 6, 0, 7, 4], [5, 11, 2, 4, 7],False, False),
# 	'conjunct-p2d': RelData([5, 4, 0, 4], [5, 3, 8, 4],False, False),
#     'determiner-p2d': RelData([5, 1, 2, 8, 4, 6, 3, 9], [6, 4, 1, 6, 10, 2, 2, 6],False, False),
#     #'i object-d2p': RelData([6], [9],False, True),
#     'noun-modifier-p2d': RelData([4, 0, 9, 5, 3, 0, 0], [5, 8, 1, 8, 3, 1, 5],False, False),
#     'num-modifier-p2d': RelData([7, 9, 1, 0], [11, 4, 10, 8],False, False),
# 	'object-p2d': RelData([7, 4, 3, 3, 0, 5, 2, 9], [10, 5, 10, 9, 8, 0, 11, 1],False, False),
# 	'other-p2d': RelData([6, 8], [9, 6],False, False),
#     'punctuation-p2d': RelData([11, 10, 2, 11, 7, 7], [6, 7, 2, 2, 8, 7],False, False),
#     'subject-p2d': RelData([7, 4], [11, 10],False, False)
#     }




# based on tiny set 10 examples
# relation_rules  = {'adj-clause-p2d': RelData([1], [1],False, False),
# 	'adj-modifier-d2p': RelData([3], [9],False, True),
# 	'adv-clause-p2d': RelData([1], [10],False, False),
# 	'adv-modifier-p2d': RelData([2], [10],False, False),
# 	'apposition-p2d': RelData([2], [1],False, False),
# 	'auxiliary-p2d': RelData([3], [8],False, False),
# 	'compound-d2p': RelData([5], [11],False, True),
# 	'conjunct-d2p': RelData([11, 4], [9, 7],False, True),
# 	'determiner-p2d': RelData([7], [9],False, False),
# 	'noun-modifier-p2d': RelData([3], [9],False, False),
# 	'num-modifier-p2d': RelData([11], [11],False, False),
# 	'object-d2p': RelData([9], [3],False, True),
# 	'other-d2p': RelData([6, 3, 5, 5], [6, 9, 9, 7],False, True),
# 	'punctuation-d2p': RelData([6, 5], [6, 0],False, True),
# 	'subject-p2d': RelData([4, 6], [10, 4],False, False)}


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
	reverse_label_map['other'] = 'dep'
	

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
				sentid += 1
				
			elif line.startswith('#'):
				if line.startswith('# sent_id'):
					out_line_ = line.strip() + '/pred'
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
				out_line_gold = line.strip()
				if fields[CONLLU_ID].isdigit() and pred is not None:
					length_sent += 1
					if fields[CONLLU_LABEL].strip() != 'root':
						col = pred.transpose()[int(fields[CONLLU_ID]) - 1]

						x = np.argwhere(col != 'no edge')
						x = x.item()
						lab = reverse_label_map[col[x][:-4]]
						
						fields[CONLLU_HEAD] = str(x + 1)
						fields[CONLLU_LABEL] = lab
						
					fields[CONLLU_POS] = ord2pos[int(fields[CONLLU_ID]) - 1]
					#fields[CONLLU_POS] = dependency.transform_label2pos(node2lab[int(fields[CONLLU_ID]) - 1])
				out_line  ='\t'.join(fields)
					
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
	for relation, rules in relation_rules2.items():
		#aggr_matrix = np.average(np.array(matrices)[rules.layers, rules.heads, :, :],weights=rules.weights, axis=0)
		aggr_matrix = np.average(np.array(matrices)[rules.layers, rules.heads, :, :], axis=0)
		aggr_matrix *= np.mean(np.array(matrices)[rules.layersT, rules.headsT, :, :], axis=0).transpose()
		#aggr_matrix /= aggr_matrix.sum(axis=0, keepdims=True)
		# if rules.d2p == True:
		# 	aggr_matrix = aggr_matrix.transpose()
		aggr_matrix = aggr_matrix/aggr_matrix.sum(axis=0,keepdims=True)/aggr_matrix.sum(axis=1, keepdims=True)
		aggr_matrix[:, root_ord] = 0.
		np.fill_diagonal(aggr_matrix, 0.)
		aggr_matrix = np.clip(aggr_matrix, 0.001, 0.999)
		aggr_matrix = np.log(aggr_matrix)
		
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
		
		if deel + '-d2p' in relation_rules2:
			dlabelm[dedge[0], dedge[1]] = deel + '-d2p'
		elif deel + '-p2d' in relation_rules2:
			dlabelm[dedge[0], dedge[1]] = deel + '-p2d'
		
		elif 'other-d2p' in relation_rules2:
			dlabelm[dedge[0], dedge[1]] = 'other-d2p'
		elif 'other-p2d' in relation_rules2:
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
	                help = "Whether it is the first iteration!")
	
	ap.add_argument("-s", "--seed", help = "To identify temp files used")
	
	ap.add_argument("-d", "--discarding", help = "Factor responisble for discarding past annotations", type=float, default=0.)
	
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
	
	rewrite_conllu(args.conllu, args.output_pred, args.output_gold,
	               f'/lnet/tspec/tmp/limisiewicz/em_params-{args.seed}.json', f'/lnet/tspec/tmp/limisiewicz/em_annotations-{args.seed}.npz',
	               break_after=200, first_iter=args.first_iteration)
