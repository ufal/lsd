#!/usr/bin/env python3

import numpy as np
import codecs
import argparse
import matplotlib.pyplot as plt
from nltk import Tree
import random
import math
import subprocess
from scipy.sparse.csgraph import minimum_spanning_tree

# size = number of tokens
# weights[i][j] = word_mixture[6][i][j] = attention weight
# wordpieces[i] = sentences_src[0][i] = wordpiece
def deptree(size, weights, wordpieces):
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

    return ('\n'.join(lines), '\n', '\n')

def staredness(size, weights, wordpieces):
    # input
    staredness = dict()
    for victim in range(size):
        staredness[victim] = sum([
            weights[voyeur][victim] for voyeur in range(size)
        ])

    # process
    # 1 means most stared upon
    result = []
    for victim in sorted(staredness, key=staredness.get, reverse=True):
        spaces = '     ' * victim
        result.append(spaces)
        result.append(wordpieces[victim])
        result.append('\n')

    return result
    
ap = argparse.ArgumentParser()
ap.add_argument("--attentions", help="NPZ file with attentions")
ap.add_argument("--labels", help="Labels separated by spaces")
ap.add_argument("--deptree", help="Output dependency trees filename stem")
ap.add_argument("--staredness", help="Output staredness filename stem")
args= ap.parse_args()

#load data
attentions_loaded = np.load(args.attentions)
sentences_count = len(attentions_loaded.files)
layers_count = attentions_loaded['att_0'].shape[0]
heads_count = attentions_loaded['att_0'].shape[1]

# iterate over sentences
for sentence_index in range(sentences_count):
    sentence_id = 'att_' + str(sentence_index)
    tokens_count = attentions_loaded[sentence_id].shape[2]
    
    word_mixture = list() 
    word_mixture.append(np.identity(tokens_count))
    # recursively compute layer weights
    for layer in range(layers_count):
        layer_matrix = np.zeros((size, size))
        head_weight_sum = 0
        for head in (range(head_count)):
            matrix = att[head]
            #softmax
            deps = np.transpose(np.exp(np.transpose(matrix)) / np.sum(np.exp(np.transpose(matrix)), axis=0))
            layer_matrix = layer_matrix + deps * head_weight
        layer_matrix = layer_matrix / heads_count
        word_mixture.append((word_mixture[layer] + layer_matrix) / 2)

sentences_src = list()
for line in labels_file:
    sentences_src.append(line.split())

#for layer in range(0,7):
for layer in range(6,7): 
    # dependency parser
    if args.deptree != None:
        with open(args.deptree, 'w') as deptree_fh:
            deptree_fh.writelines(
                    deptree(size, word_mixture[6], sentences_src[0])
                    )
        print("Dep tree written.")

    # staredness -- how much words are stared upon :-)
    if args.staredness != None:
        with open(args.staredness, 'w') as staredness_fh:
            staredness_fh.writelines(
                    staredness(size, word_mixture[6], sentences_src[0])
                    )
        print("Staredness written.")
