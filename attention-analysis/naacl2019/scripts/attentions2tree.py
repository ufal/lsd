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
ap.add_argument("-a", "--attentions", required=True,
        help="NPZ file with attentions")
ap.add_argument("-t", "--tokens", required=True,
        help="Labels (tokens) separated by spaces")
ap.add_argument("-d", "--deptrees",
        help="Output unoriented dep trees into this file")
ap.add_argument("-v", "--visualizations",
        help="Output heatmap prefix")
ap.add_argument("-k", "--heads", nargs='+', type=int,
        help="Only use the specified head(s) from the last layer; 0-based")
#ap.add_argument("-l", "--layers", nargs='+', default=[-1],
ap.add_argument("-l", "--layer", default=-1, type=int,
        help="Only use the specified layer; 1-based")
ap.add_argument("-s", "--sentences", nargs='+', type=int, default=[4,5,6],
        help="Only use the specified sentences; 0-based")
ap.add_argument("-e", "--eos", action="store_true",
        help="Attentions contain EOS")
ap.add_argument("-n", "--noaggreg", action="store_true",
        help="Do not aggregate the attentions over layers, just use one layer")
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
if args.deptrees:
    deptrees = open(args.deptrees, 'w')

# iterate over sentences
for sentence_index in range(sentences_count):
    # option to only process selected sentences
    if args.sentences and sentence_index in args.sentences:
        print('Processing sentence', sentence_index, file=sys.stderr)
    else:
        continue
    
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
            #HACK
            # TODO maybe this is bad, esp. if multiple values are high
            # TODO do the max trick -- for each column (or row ????) subtract its max
            # from all of its components to get the values into (-inf, 0]
            # but this leads to underflows for low values, so maybe even
            # better is to subtract max and then add 80, to get it into (-inf, 80]
            matrix = np.minimum(matrix, np.ones((tokens_count,tokens_count)) * 80.0)
            matrix = np.maximum(matrix, np.ones((tokens_count,tokens_count)) * -80.0)
            exp_matrix = np.exp(matrix)
            deps = np.transpose(np.transpose(exp_matrix) / np.sum(exp_matrix, axis=1))
            layer_matrix = layer_matrix + deps
            #if sentence_index == 6:
            #print(np.min(matrix),file=sys.stderr)
            #print("EXPMIN:"  + str(np.exp(np.min(matrix))),file=sys.stderr)
            #print(deps, file=sys.stderr)
        # avg
        layer_matrix = layer_matrix / heads_count
        # next layer = avg of this layer and prev layer
        word_mixture.append((np.matmul(word_mixture[layer], layer_matrix) + word_mixture[layer]) / 2)
        #if sentence_index == 6:
           #print("LM")
           #print(layer_matrix)
           #print("WM")
           #print(word_mixture[-1])

    # compute trees
    if deptrees:
        tree = deptree(np.transpose(word_mixture[args.layer]), tokens_list)
        print(tree, file=deptrees)

    # draw heatmaps
    if args.visualizations:
        for layer in range(layers_count + 1):
            # +1 because word_mixture[0] is the initial identity matrix
            heatmap(word_mixture[layer], "", "", "", tokens_list, tokens_list)
            plt.savefig(args.visualizations + str(sentence_index) + '-l' + str(layer) + '.png', dpi=200, format='png', bbox_inches='tight')
            plt.close()

if deptrees:
    deptrees.close()

