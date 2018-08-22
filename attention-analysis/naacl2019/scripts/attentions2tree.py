#!/usr/bin/env python3

import numpy as np
import codecs
import argparse
import matplotlib
matplotlib.use('Agg')
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
        help="Output unori dep trees into this file")
ap.add_argument("-o", "--oritrees",
        help="Output oriented dep trees into this file")
ap.add_argument("-v", "--visualizations",
        help="Output heatmap prefix")

ap.add_argument("-l", "--layer", type=int, default=-1,
        help="Only use the specified layer; 0-based")
ap.add_argument("-k", "--head", type=int, default=-1,
        help="Only use the specified head from the last layer; 0-based")
ap.add_argument("-s", "--sentences", nargs='+', type=int, default=[4,5,6],
        help="Only use the specified sentences; 0-based")

ap.add_argument("-D", "--sentences_as_dirs", action="store_true",
        help="Store images into separate directories for each sentence")
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
            for row in range(size):
                # MINIMUM spanning tree
                # now sum
                # TODO max
                score = - weights[row][brother] * weights[row][sister]
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

def oritree(weights, wordpieces):
    size = len(wordpieces)

    # non-optimal greedy MST algorithm
    heads = dict()
    headweights = dict()
    nodes = set(range(size))
    # find root node
    root = np.argmax(np.diag(weights))
    heads[root] = -1
    headweights[root] = weights[root][root]
    nodes.remove(root)
    # construct tree
    while nodes:
        # find best child to attach into the partial tree
        best_weight = -1
        best_parent = -1
        best_child  = -1
        # children = not yet attached nodes
        for child in nodes:
            # parents = already attached nodes
            for parent in heads.keys():
                weight = weights[child][parent]
                if weight > best_weight:
                    best_weight = weight
                    best_child  = child
                    best_parent = parent
        # attach best child
        assert best_child != -1
        heads[best_child] = best_parent
        headweights[best_child] = best_weight
        nodes.remove(best_child)
    # conll-like output
    lines = []
    for child in range(size):
        # 5    the_    3
        lines.append('\t'.join((
            str(child + 1),
            wordpieces[child],
            str(heads[child] + 1),
            str(round(headweights[child], 2)),
            wordpieces[heads[child]],
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

def write_heatmap(tokens_list, sentence_index, vis, layer, aggreg, head=-1):
    filename = ''
    if args.sentences_as_dirs:
        filename += "s" + str(sentence_index) + "/"
    filename += args.visualizations
    if not args.sentences_as_dirs:
        filename += "s" + str(sentence_index) + '-'
    if aggreg == 0:
        filename += 'n-'
    if head == -1:
        filename += 'kall-'
    else:
        filename += 'k' + str(head) + '-'
    filename += 'l' + str(layer)
    filename += '.png'

    heatmap(vis[layer][aggreg][head], "", "", "", tokens_list, tokens_list)
    plt.savefig(filename, dpi=200, format='png', bbox_inches='tight')
    plt.close()

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
else:
    deptrees = None
if args.oritrees:
    oritrees = open(args.oritrees, 'w')
else:
    oritrees = None

# recursively aggregated -- attention over input tokens
def wm_aggreg(this_layer, last_layer):
    return (np.matmul(this_layer, last_layer) + last_layer) / 2

# this layer and residual connection -- attention over positions
def wm_avg(this_layer, first_layer):
    return (this_layer + first_layer) / 2


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
    # for visualisation -- vis[layer][aggreg][head]
    vis = list()
    for layer in range(layers_count):
        layer_deps = list()  # for vis
        layer_matrix = np.zeros((tokens_count, tokens_count))
        for head in range(heads_count):
            matrix = attentions_loaded[sentence_id][layer][head]
            # the max trick -- for each row subtract its max
            # from all of its components to get the values into (-inf, 0]            
            matrix = np.transpose(np.transpose(matrix) - np.max(matrix, axis=1))
            # softmax
            exp_matrix = np.exp(matrix)
            deps = np.transpose(np.transpose(exp_matrix) / np.sum(exp_matrix, axis=1))
            layer_deps.append(deps)
            layer_matrix = layer_matrix + deps
        # avg
        layer_matrix = layer_matrix / heads_count
        layer_deps.append(layer_matrix)
        # next layer = avg of this layer and prev layer
        # TODO add head weights from ff matrices
        vis.append([
                [wm_avg(m, word_mixture[0]) for m in layer_deps],
                [wm_aggreg(m, word_mixture[layer]) for m in layer_deps],
                ])
        word_mixture.append( wm_aggreg(layer_matrix, word_mixture[layer]) )

        #if sentence_index == 6:
           #print("LM")
           #print(layer_matrix)
           #print("WM")
           #print(word_mixture[-1])

    # compute trees
    if deptrees:
        # print("Deptrees disabled!", file=sys.stderr)
        # tree = deptree(np.transpose(word_mixture[-1]), tokens_list)
        aggreg = 0 if args.noaggreg else 1
        tree = deptree(vis[args.layer][aggreg][args.head], tokens_list)
        print(tree, file=deptrees)

    if oritrees:
        # print("Deptrees disabled!", file=sys.stderr)
        # tree = deptree(np.transpose(word_mixture[-1]), tokens_list)
        aggreg = 0 if args.noaggreg else 1
        tree = oritree(vis[args.layer][aggreg][args.head], tokens_list)
        print(tree, file=oritrees)

    # draw heatmaps
    if args.visualizations != None:
        for layer in range(layers_count):
            write_heatmap(tokens_list, sentence_index, vis, layer, 0)
            write_heatmap(tokens_list, sentence_index, vis, layer, 1)
            for head in range(heads_count):
                write_heatmap(tokens_list, sentence_index, vis, layer, 0, head)
                write_heatmap(tokens_list, sentence_index, vis, layer, 1, head)

if deptrees:
    deptrees.close()
if oritrees:
    oritrees.close()

