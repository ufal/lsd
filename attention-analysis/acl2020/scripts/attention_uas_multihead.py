import numpy as np
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt
from tqdm import tqdm
from copy import copy

from tools import dependency, sentence_attentions
from tools.dependency_converter import DependencyConverter
TOP_HEADS_NUM = 25


def average_heads(all_matrices, ls, hs):
	# NOTE 8: softamx after averaging
	# matrix = np.average(all_matrices[ls, hs, :, :], axis=0)
	# matrix = matrix - np.max(matrix, axis=1, keepdims=True)
	# # softmax
	# exp_matrix = np.exp(matrix)
	# return exp_matrix / np.sum(exp_matrix, axis=1, keepdims=True)
	return np.average(all_matrices[ls, hs, :, :], axis=0)


def uas_from_matrices(matrices, dep_rels, all_posmasks):
	retrived = defaultdict(int)
	total = defaultdict(int)
	for matrix, dep_rel, pos_masks in zip(matrices, dep_rels, all_posmasks):
		for rel_type, rel_pairs in dep_rel.items():
			if rel_type not in pos_masks:
				retr_pairs = {}
			else:
				retr_pairs = set(zip(range(matrix.shape[0]), np.argmax(matrix * pos_masks[rel_type], axis=1)))
			retrived[rel_type] += len(set(rel_pairs).intersection(retr_pairs) )
			total[rel_type] += len(set(rel_pairs))
	
	for k in sorted(retrived.keys()):
		if total[k] > 0:
			print(f"UAS for {k} : {retrived[k]/total[k]} (number of relations: {total[k]})")
		else:
			print(f"No relations for {k}")


def uas_from_matrices_rel(matrices, dep_rels, rel_type, all_posmasks):
	retrived = 0.
	total = 0.
	for matrix, dep_rel, pos_masks in zip(matrices, dep_rels, all_posmasks):
		retr_pairs = set(zip(range(matrix.shape[0]), np.argmax(matrix * pos_masks[rel_type], axis=1)))
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
	ap.add_argument("-T", "--train-conllu", help="Conllu file for training POS",
	                default='/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/entrain.conllu')
	
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
	
	
	grouped_tokens, _ = dependency.group_wordpieces(tokens_loaded, args.conllu)
	
	# NOTE 8 : softmax after averaging
	#no_softmax = True
	
	no_softmax  = args.no_softmax
	attention_gen = sentence_attentions.generate_matrices(attentions_loaded, grouped_tokens, args.eos, no_softmax,
	                                                      args.maxlen, args.sentences)
	
	dependency_rels_labeled = dependency.read_conllu_labeled(args.conllu, convert=True)
	pos_frame = dependency.conllu2freq_frame(args.train_conllu)
	
	all_metrices = []
	all_pos_masks = []
	sentences_considered = []
	for vis, idx in tqdm(attention_gen):
		if vis:
			sentences_considered.append(idx)
			pos_masks = dict()
			diag_mask = sentence_attentions.diagonal_mask(dependency_rels_labeled[idx])
			for k in uas.keys():
				rel_number[k][idx, 0, 0] = len(dependency_rels[idx][k])
				#pos_masks[k] = sentence_attentions.pos_soft_mask(dependency_rels_labeled[idx], k, pos_frame)
				# NOTE 10: hard mask used
				#pos_masks[k] = sentence_attentions.pos_hard_mask(dependency_rels_labeled[idx], k, pos_frame, thr=0.01)
			
				pos_masks[k] = diag_mask
			for layer in range(layers_count):
				for head in range(heads_count):
					# deps = vis[layer][head]
					# deps = (deps == deps.max(axis=1)[:, None]).astype(int)
					for k in uas.keys():
						deps = vis[layer][head] * pos_masks[k]
						deps = (deps == deps.max(axis=1)[:, None]).astype(int)
						if len(dependency_rels[idx][k]):
							uas[k][idx, layer, head] \
								= np.sum(deps[tuple(zip(*dependency_rels[idx][k]))])
			all_metrices.append(vis)
			all_pos_masks.append(pos_masks)
	
	dependency_rels = [dependency_rels[idx] for idx in sentences_considered]

	for k in uas.keys():
		uas[k] = uas[k][sentences_considered, :, :]
		rel_number[k] = rel_number[k][sentences_considered, :, :]

	all_uas = defaultdict(list)
	best_head_mixture = dict()
	max_uas = dict()
	for k in tqdm(sorted(uas.keys())):
		uas[k] = np.sum(uas[k], axis=0) / np.sum(rel_number[k], axis=0)
		
		top_heads_ids = np.argsort(uas[k], axis=None)[-TOP_HEADS_NUM:][::-1]
		picked_heads_ids = []
		max_uas[k] = - np.inf
		for num in range(0,TOP_HEADS_NUM):
			curr_heads_ids = picked_heads_ids + [top_heads_ids[num]]
			curr_lids, curr_hids = np.unravel_index(curr_heads_ids, uas[k].shape)
			avg_gen = (average_heads(np.array(c_m),curr_lids, curr_hids ) for c_m in all_metrices)
			curr_uas = uas_from_matrices_rel(avg_gen, dependency_rels, k, all_pos_masks)
			all_uas[k].append(curr_uas)
			if curr_uas > max_uas[k]:
				max_uas[k] = curr_uas
				picked_heads_ids = curr_heads_ids
				best_head_mixture[k] = np.unravel_index(picked_heads_ids, uas[k].shape)
				
		print('\n*****\n')
		print(f"Best uas for: {k} : {max_uas[k]}")
		print(f"Head mixture : {best_head_mixture[k]}")
		best_gen = (average_heads(np.array(c_m), best_head_mixture[k][0], best_head_mixture[k][1]) for c_m in all_metrices)
		uas_from_matrices(best_gen, dependency_rels, all_pos_masks)
		
	print_next = []
	for k in tqdm(sorted(max_uas.keys())):
		if k.endswith('d2p'):
			alt_k = k[:-4] + '-p2d'
			if max_uas[k] > max_uas[alt_k]:
				print(f"'{k}': RelData({list(best_head_mixture[k][0])}, {list(best_head_mixture[k][1])},False, True),")
				print_next.append(f"'{alt_k}': RelData({list(best_head_mixture[alt_k][0])}, {list(best_head_mixture[alt_k][1])},False, False),")
			else:
				print(f"'{alt_k}': RelData({list(best_head_mixture[alt_k][0])}, {list(best_head_mixture[alt_k][1])},False, False),")
				print_next.append(f"'{k}': RelData({list(best_head_mixture[k][0])}, {list(best_head_mixture[k][1])},False, True),")
				
	print("worse relations")
	print("\n".join(print_next))
	for k in sorted(uas.keys()):
		uas_filename = f'{args.uas}-{k}.{args.format}'
		
		plot_uas(all_uas[k], f"Accuracy for {k}", "number best heads averaged", "accuracy", "green")

		plt.savefig(uas_filename, dpi=200, format=args.format)
		plt.close()
