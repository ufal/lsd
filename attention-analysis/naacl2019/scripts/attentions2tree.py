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
ap.add_argument("-d", "--deptrees", help="Output unoriented dep trees into this file")
ap.add_argument("-h", "--heatmaps", help="Output heatmap prefix")
ap.add_argument("-e", "--eos", help="Attentions contain EOS", action="store_true")
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

    # end of sentence
    lines.append('')

    return '\n'.join(lines)

def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels):
    '''
    Copied form:
    https://stackoverflow.com/questions/20574257/constructing-a-co-occurrence-matrix-in-python-pandas
    '''
    # Plot it out
    fig, ax = plt.subplots()    
    c = ax.pcolor(AUC, edgecolors='k', linestyle= 'dashed', linewidths=0.2, cmap='pink', vmin=0.0, vmax=1.0)
    
    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(AUC.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(AUC.shape[1]) + 0.5, minor=False)
    
    # set tick labels
    xfont = {'family': 'serif', 'weight': 'normal', 'size': 8, 'rotation' : 'vertical'}
    yfont = {'family': 'serif', 'weight': 'normal', 'size': 8}
    #ax.set_xticklabels(np.arange(1,AUC.shape[1]+1), minor=False)
    ax.set_xticklabels(xticklabels, minor=False, fontdict=xfont)
    ax.set_yticklabels(yticklabels, minor=False, fontdict=yfont)
    
    # set title and x/y labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)      

    # Remove last blank column
    plt.xlim( (0, AUC.shape[1]) )

    # Turn off all the ticks
    ax = plt.gca()    
    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    # Add color bar
    plt.colorbar(c)

    # Add text in each cell 
    #show_values(c)

    # Proper orientation (origin at the top left instead of bottom left)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    # resize 
    fig = plt.gcf()
    #fig.set_size_inches(cm2inch(40, 20))


#load data
attentions_loaded = np.load(args.attentions)
sentences_count = len(attentions_loaded.files)
layers_count = attentions_loaded['arr_0'].shape[0]
heads_count = attentions_loaded['arr_0'].shape[1]
with open(args.tokens) as tokens_file:
    tokens_loaded = [l.split() for l in tokens_file]

# outputs
deptrees = list()

# iterate over sentences
for sentence_index in range(sentences_count):
    sentence_id = 'arr_' + str(sentence_index)
    tokens_count = attentions_loaded[sentence_id].shape[2]
    tokens_list = tokens_loaded[sentence_index]
    if args.eos:
        tokens_list.append('EOS')
    # NOTE sentences truncated to 64 tokens
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
            #deps = np.transpose(np.exp(np.transpose(matrix)) / np.sum(np.exp(np.transpose(matrix)), axis=0)) # puvodni
            #deps = np.exp(matrix) / np.sum(np.exp(matrix), axis=0) # puvodni bez transpose
            #exp_matrix = np.exp(matrix - np.amax(matrix, axis=0))
            #deps = exp_matrix / np.sum(exp_matrix, axis=0)
            exp_matrix = np.exp(matrix)
            deps = exp_matrix / np.sum(exp_matrix, axis=1)
            layer_matrix = layer_matrix + deps
        # avg
        layer_matrix = layer_matrix / heads_count
        # next layer = avg of this layer and prev layer
        word_mixture.append((np.matmul(word_mixture[layer], layer_matrix) + word_mixture[layer]) / 2)

    # compute trees
    if args.deptrees:
        tree = deptree(np.transpose(word_mixture[6]), tokens_list)
        deptrees.append(tree)
        #print('# sentence', sentence_index)
        #print(tree)
        #print()

    # draw heatmaps
    # so far only for the first sentence
    if args.heatmaps and sentence_index == 0:
        for layer in range(layers_count + 1):
            # +1 because word_mixture[0] is the initial identity matrix
            heatmap(word_mixture[layer]), "", "", "", token_list, token_list)
            plt.savefig(args.heatmaps + str(sentence_index) + '-l' + str(layer) + '.pdf', dpi=300, format='pdf', bbox_inches='tight')

if args.deptrees:
    with open(args.deptrees, 'w') as output:
        print(*deptrees, sep='\n', file=output)



