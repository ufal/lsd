import numpy as np
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt

from tools import dependency, sentence_attentions

TOP_HEADS_NUM = 25


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
	
	for k in sorted(retrived.keys()):
		if total[k] > 0:
			print(f"UAS for {k} : {retrived[k]/total[k]} (number of relations: {total[k]})")
		else:
			print(f"No relations for {k}")


def uas_from_matrices_rel(matrices, dep_rels, rel_type):
	retrived = 0.
	total = 0.
	for matrix, dep_rel in zip(matrices, dep_rels):
		retr_pairs = set(zip(range(matrix.shape[0]), np.argmax(matrix, axis=1)))
		rel_pairs = dep_rel[rel_type]
		retrived += len(set(rel_pairs).intersection(retr_pairs))
		total += len(set(rel_pairs))
		
	if total == 0:
		return 0.
	
	return float(retrived)/float(total)


def plot_uas(uas, title, xlabel, ylabel, color='lightblue'):

	fig, ax = plt.subplots(1, 1, figsize=(16, 6))
	ax.plot(range(len(uas)),uas, color=color)

	fig.suptitle(title)
	
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)


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
	
	grouped_tokens, _ = dependency.group_wordpieces(tokens_loaded, args.conllu)
	
	attention_gen = sentence_attentions.generate_matrices(attentions_loaded, grouped_tokens, args.eos, args.no_softmax,
	                                                      args.maxlen, args.sentences)
	
	sentences_considered = []
	for vis, idx in attention_gen:
		sentences_considered.append(idx)
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
	
	dependency_rels = [dependency_rels[idx] for idx in sentences_considered]
	for k in uas.keys():
		uas[k] = uas[k][sentences_considered, :, :]
		rel_number[k] = rel_number[k][sentences_considered, :, :]

	all_uas = defaultdict(list)
	best_head_mixture = dict()
	for k in sorted(uas.keys()):
		uas[k] = np.sum(uas[k], axis=0) / np.sum(rel_number[k], axis=0)
		
		top_heads_ids = np.argsort(uas[k], axis=None)[-TOP_HEADS_NUM:][::-1]
		picked_heads_ids = []
		max_uas = - np.inf
		for num in range(0,TOP_HEADS_NUM):
			curr_heads_ids = picked_heads_ids + [top_heads_ids[num]]
			curr_lids, curr_hids = np.unravel_index(curr_heads_ids, uas[k].shape)
			avg_gen = (average_heads(np.array(c_m),curr_lids, curr_hids ) for c_m in all_metrices)
			curr_uas = uas_from_matrices_rel(avg_gen, dependency_rels, k)
			all_uas[k].append(curr_uas)
			if curr_uas > max_uas:
				max_uas = curr_uas
				picked_heads_ids = curr_heads_ids
				best_head_mixture[k] = np.unravel_index(picked_heads_ids, uas[k].shape)
				
		print('\n*****\n')
		print(f"Best uas for: {k} : {max_uas}")
		print(f"Head mixture : {best_head_mixture[k]}")
		best_gen = (average_heads(np.array(c_m), best_head_mixture[k][0], best_head_mixture[k][1]) for c_m in all_metrices)
		uas_from_matrices(best_gen, dependency_rels)
		
	for k in sorted(uas.keys()):
		uas_filename = f'{args.uas}-{k}.{args.format}'
		
		plot_uas(all_uas[k], f"Accuracy for {k}", "number best heads averaged", "accuracy", "green")

		plt.savefig(uas_filename, dpi=200, format=args.format)
		plt.close()
