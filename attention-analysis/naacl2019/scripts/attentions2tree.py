#!/usr/bin/env python3

import numpy as np
import codecs
import argparse
import matplotlib.pyplot as plt
from nltk import Tree
import random
import math
import subprocess
import sys
from scipy.sparse.csgraph import minimum_spanning_tree

ap = argparse.ArgumentParser()
ap.add_argument("-a", "--attentions", help="NPZ file with attentions", required=True)
ap.add_argument("-t", "--tokens", help="Labels (tokens) separated by spaces", required=True)
args= ap.parse_args()

# weights[i][j] = word_mixture[6][i][j] = attention weight
# wordpieces = list of tokens
def deptree(weights, wordpieces):
    size = len(wordpieces)
    graph = [ [0] * size for i in range(size)  ]
    for brother in range(size-1):
        for sister in range(brother+1, size-1):
            for column in range(size):
                # MINIMUM spanning tree
                # now sum
                # TODO max
                score = - weights[column][brother] * weights[column][sister]
                graph[brother][sister] += score

    mst = minimum_spanning_tree(graph).toarray()

    lines = []
    for brother in range(size-1):
        sisters = []
        for sister in range(brother+1, size-1):
            if mst[brother][sister] != 0 or mst[sister][brother] != 0:
                sisters.append(str(sister))
        # 5    the_    3,4,6
        lines.append('\t'.join((
            str(brother), wordpieces[brother], ','.join(sisters)
        )))

    return '\n'.join(lines)

#load data
attentions_loaded = np.load(args.attentions)
sentences_count = len(attentions_loaded.files)
layers_count = attentions_loaded['arr_0'].shape[0]
heads_count = attentions_loaded['arr_0'].shape[1]
with open(args.tokens) as tokens_file:
    tokens_loaded = [l.split() for l in tokens_file]

# iterate over sentences
for sentence_index in range(sentences_count):
    sentence_id = 'arr_' + str(sentence_index)
    tokens_count = attentions_loaded[sentence_id].shape[2]
    # TODO add EOS token at end of each tokens list
    tokens_list = tokens_loaded[sentence_index]
    # TODO sentences truncated to 64 tokens it seems
    # assert len(tokens_list) == tokens_count, "Bad no of tokens in sent " + str(sentence_index)
    assert len(tokens_list) >= tokens_count, "Bad no of tokens in sent " + str(sentence_index)
    if len(tokens_list) > tokens_count:
        print('Truncating tokens from ', len(tokens_list), 'to', tokens_count,
                'on line', sentence_index, '(0-based indexing)', file=sys.stderr)
        tokens_list = tokens_list[:tokens_count]

    # recursively compute layer weights
    word_mixture = list() 
    word_mixture.append(np.identity(tokens_count))
    for layer in range(layers_count):
        layer_matrix = np.zeros((tokens_count, tokens_count))
        for head in range(heads_count):
            matrix = attentions_loaded[sentence_id][layer][head]
            #softmax
            deps = np.transpose(np.exp(np.transpose(matrix)) / np.sum(np.exp(np.transpose(matrix)), axis=0))
            layer_matrix = layer_matrix + deps
        # avg
        layer_matrix = layer_matrix / heads_count
        # next layer = avg of this layer and prev layer
        word_mixture.append((word_mixture[layer] + layer_matrix) / 2)

    # compute trees
    tree = deptree(word_mixture[6], tokens_list)
    print('# sentence', sentence_index)
    print(tree)
    print()


