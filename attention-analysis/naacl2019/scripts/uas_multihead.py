import numpy as np
import sys
import argparse
from collections import defaultdict
import matplotlib
import matplotlib.pyplot as plt

import dependency


def average_heads(all_matrices, ls, hs):
	return np.average(all_matrices[ls, hs, :, :], axis=0)


def uas_from_matrices(matrices, dep_rels):
	retrived = defaultdict(int)
	total = defaultdict(int)
	for matrix, dep_rel in zip(matrices, dep_rels):
		retr_pairs = set(zip(range(matrix.shape[0]), np.argmax(matrix, axis=1)))
		for rel_type, rel_pairs in dep_rel.items():
			retrived[rel_type] += len(set(rel_pairs).intersection(retr_pairs) )
			total[rel_type] += len(set(rel_pairs))
	
	for k in retrived.keys():
		print(f"UAS for {k} : {retrived[k]/total[k]} (number of relations: {total[k]})")


def uas_from_matrices_rel(matrices, dep_rels, rel_type):
	retrived = 0.
	total = 0.
	for matrix, dep_rel in zip(matrices, dep_rels):
		retr_pairs = set(zip(range(matrix.shape[0]), np.argmax(matrix, axis=1)))
		for rel_pairs in dep_rel[rel_type]:
			retrived += len(set(rel_pairs).intersection(retr_pairs))
			total += len(set(rel_pairs))
	
	return float(retrived)/float(total)


def aggregate_subtoken_matrix(attention_matrix, wordpieces):
	# this functions connects subtokens and aggregates their attention.
	aggregate_wps = []
	wp_ids = []
	for wp_id, wp in enumerate(wordpieces):
		wp_ids.append(wp_id)
		if not wp.endswith('@@'):
			aggregate_wps.append(wp_ids)
			wp_ids = []
	
	midres_matrix = np.zeros((len(aggregate_wps), len(wordpieces)))
	
	for tok_id, wp_ids in enumerate(aggregate_wps):
		midres_matrix[tok_id,: ] = np.mean(attention_matrix[wp_ids, :], axis=0)
	
	res_matrix = np.zeros((len(aggregate_wps), len(aggregate_wps)))
	
	for tok_id, wp_ids in enumerate(aggregate_wps):
		res_matrix[:, tok_id] = np.sum(midres_matrix[:, wp_ids], axis=1)
	
	words = ' '.join(wordpieces).replace('@@ ', '')
	res_tokens = words.split()
	
	assert len(res_tokens) == len(aggregate_wps), "Result matrix and token dimesnions don't match"
	return res_matrix


def generate_deps(attentions_loaded, tokens_loaded, eos=True, no_softmax=False, maxlen=1000):
	sentences_count = len(tokens_loaded)
	layers_count = attentions_loaded['arr_0'].shape[0]
	heads_count = attentions_loaded['arr_0'].shape[1]
	for sentence_index in range(sentences_count):
		sentence_id = 'arr_' + str(sentence_index)
		tokens_count = attentions_loaded[sentence_id].shape[2]
		
		
		if eos:
			tokens_count -= 1
		tokens_list = tokens_loaded[sentence_index]
		
		# check maxlen
		words = ' '.join(tokens_list).replace('@@ ', '')
		
		words_list = words.split()
		if not len(words_list) <= maxlen:
			print('Too long sentence, skipped', sentence_index, file=sys.stderr)
			continue
		
		# NOTE sentences truncated to 64 tokens
		# assert len(tokens_list) == tokens_count, "Bad no of tokens in sent " + str(sentence_index)
		assert len(tokens_list) >= tokens_count, "Bad no of tokens in sent " + str(sentence_index)
		if len(tokens_list) > tokens_count:
			print('Too long sentence, skipped', sentence_index, file=sys.stderr)
			continue
		
		words_count = len(words_list)
		
		# for visualisation -- vis[layer][head]
		vis = list()
		
		for layer in range(layers_count):
			layer_deps = list()  # for vis
			for head in range(heads_count):
				matrix = attentions_loaded[sentence_id][layer][head]
				if eos:
					matrix = matrix[:-1, :-1]
				# the max trick -- for each row subtract its max
				# from all of its components to get the values into (-inf, 0]
				if not no_softmax:
					matrix = matrix - np.max(matrix, axis=1, keepdims=True)
					# softmax
					exp_matrix = np.exp(matrix)
					deps = exp_matrix / np.sum(exp_matrix, axis=1, keepdims=True)
				else:
					deps = matrix / np.sum(matrix, axis=1, keepdims=True)
				deps = aggregate_subtoken_matrix(deps, tokens_list)
				layer_deps.append(deps)
			# layer_matrix = layer_matrix + deps
			vis.append(layer_deps)
		yield vis


def plot_uas(uas, title, xlabel, ylabel, color='lightblue'):

	fig, ax = plt.subplots(1, 1, figsize=(16, 6))
	ax.plot(range(len(uas)),uas, color=color)

	fig.suptitle(title)
	
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	ax.invert_yaxis()


if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-a", "--attentions", required=True, help="NPZ file with attentions")
	ap.add_argument("-t", "--tokens", required=True, help="Labels (tokens) separated by spaces")
	
	ap.add_argument("-u", "--uas", help="Output uas measuere into this file")
	ap.add_argument("-c", "--conllu", help="Eval against the given conllu faile")
	
	ap.add_argument("-f", "--format", default="png",
	                help="Output visualisation as this format (pdf, png, maybe other options)")
	ap.add_argument("-F", "--fontsize", default=8, type=int,
	                help="Fontsize for heatmap; 8 is good for png. 10 is good for PDF it seems")
	
	ap.add_argument("-s", "--sentences", nargs='*', type=int, default=None,
	                help="Only use the specified sentences; 0-based")
	ap.add_argument("-m", "--maxlen", type=int, default=1000,
	                help="Skip sentences longer than this many words. A word split into several wordpieces is counted as one word. EOS is not counted.")
	
	ap.add_argument("-e", "--eos", action="store_true",
	                help="Attentions contain EOS")
	
	ap.add_argument("-n", "--no-softmax", action="store_true",
	                help="Whether not to use softmax for attention matrices, use with bert metrices")
	
	args = ap.parse_args()
	
	attentions_loaded = np.load(args.attentions)
	sentences_count = len(attentions_loaded.files)
	layers_count = attentions_loaded['arr_0'].shape[0]
	heads_count = attentions_loaded['arr_0'].shape[1]
	
	with open(args.tokens) as tokens_file:
		tokens_loaded = [l.split() for l in tokens_file]
	
	# in dependency_rels for each sentece there is a lists of tuples (token, token's head)
	# in dependency_rels_rev tuples are reversed.
	dependency_rels = dependency.read_conllu(args.conllu, directional=True)
	
	uas = {aggr: np.zeros((sentences_count, layers_count, heads_count))
	       for aggr in dependency.labels}
	
	rel_number = {aggr: np.zeros((sentences_count, 1, 1)) for aggr in dependency.labels}
	
	
	all_metrices = list()
	
	for idx, vis in enumerate(generate_deps(attentions_loaded, tokens_loaded, args.eos, args.no_softmax, args.maxlen)):
		for k in uas.keys():
			rel_number[k][idx, 0, 0] = len(dependency_rels[idx][k])
		for layer in range(layers_count):
			for head in range(heads_count):
				deps = vis[layer][head]
				deps = (deps == deps.max(axis=1)[:, None]).astype(int)
				for k in uas.keys():
					if len(dependency_rels[idx][k]):
						uas[k][idx, layer, head] \
							= np.sum(deps[tuple(zip(*dependency_rels[idx][k]))])
		all_metrices.append(vis)

	all_uas = defaultdict(list)
	best_head_mixture = dict()
	for k in uas.keys():
		uas[k] = np.sum(uas[k], axis=0) / np.sum(rel_number[k], axis=0)
		
		best_heads_ids = np.argsort(uas[k], axis=None)[-10:][::-1]
		max_uas = - np.inf
		for num in range(10):
			considered_heads = np.unravel_index(best_heads_ids[:num], uas[k].shape)
			avg_gen = (average_heads(np.array(c_m), considered_heads[0], considered_heads[1]) for c_m in all_metrices)
			curr_uas = uas_from_matrices_rel(avg_gen, dependency_rels, k)
			all_uas[k].append(curr_uas)
			if curr_uas > max_uas:
				max_uas = curr_uas
				best_head_mixture[k] = considered_heads
				
		print('\n*****\n')
		print(f"Best uas for: {k} : {max_uas}")
		print(f"Head mixture : {best_head_mixture[k]}")
		best_gen = (average_heads(np.array(c_m), best_head_mixture[k][0], best_head_mixture[k][1]) for c_m in all_metrices)
		uas_from_matrices(best_gen, dependency_rels)
		
	for k in uas.keys():
		uas_filename = f'{args.uas}-{k}.{args.format}'
		
		plot_uas(all_uas[k], f"Accuracy for {k}", "number best heads averaged", "accuracy", "green")

		plt.savefig(uas_filename, dpi=200, format=args.format)
		plt.close()
