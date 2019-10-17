# tom lim
# my approach:
#   - eos token is omitted (attention avaraged for the rest of tokens)
#   - subtoken attentions are averaged

import argparse
import numpy as np


def aggregate_subtoken_matrix(attention_matrix, wordpieces):
	aggregate_wps = []
	wp_ids = []
	for wp_id, wp in enumerate(wordpieces):
		wp_ids.append(wp_id)
		if wp.endswith('@@'):
			aggregate_wps.append(wp_ids)
			wp_ids = []

	midres_matrix = np.zeros((len(wordpieces), len(aggregate_wps)))
	
	for tok_id, wp_ids in enumerate(aggregate_wps):
		midres_matrix[tok_id,: ] = np.mean(attention_matrix[wp_ids, :], axis=0, keepdims=True)
	
	res_matrix = np.zeros((len(aggregate_wps), len(aggregate_wps)))
	
	for tok_id, wp_ids in enumerate(aggregate_wps):
		res_matrix[:, tok_id] = np.sum(midres_matrix[:, wp_ids], axis=1, keepdims=True)
	
	words = ' '.join(wordpieces).replace('@@ ', '')
	res_tokens = words.split()
	
	assert len(res_tokens) == len(aggregate_wps), "Result matrix and token dimesnions don't match"
	return res_matrix, res_tokens


if __name__ == 'main':
	ap = argparse.ArgumentParser()
	ap.add_argument("-a", "--attentions", required=True, help="NPZ file with attentions")
	ap.add_argument("-t", "--tokens", required=True, help="Labels (tokens) separated by spaces")
	
	ap.add_argument("-d", "--depal", help="Output deep alignment measuere into this file")
	ap.add_argument("-c", "--conllu", help="Eval against the given conllu faile")
	
	ap.add_argument("-f", "--format", default="png", 
	                help="Output visualisation as this format (pdf, png, maybe other options)")
	ap.add_argument("-F", "--fontsize", default=8, type=int, 
	                help="Fontsize for heatmap; 8 is good for png. 10 is good for PDF it seems")
	
	ap.add_argument("-s", "--sentences", nargs='+', type=int, default=[4, 5, 6],
	                help="Only use the specified sentences; 0-based")
	ap.add_argument("-m", "--maxlen", type=int, default=1000,
	                help="Skip sentences longer than this many words. A word split into several wordpieces is counted as one word. EOS is not counted.")
	
	ap.add_argument("-e", "--eos", action="store_true",
	                help="Attentions contain EOS")
	
	args = ap.parse_args()
