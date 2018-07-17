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
    
def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels):
    '''
    Inspired by:
    - http://stackoverflow.com/a/16124677/395857 
    - http://stackoverflow.com/a/25074150/395857
    
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

ap = argparse.ArgumentParser()
ap.add_argument("--attentions", help="NPZ file with attentions")
ap.add_argument("--weights", help="NPZ file with projection weights")
ap.add_argument("--alignment", help="Alignment to the PTB tokens")
ap.add_argument("--labels", help="Labels separated by spaces")
ap.add_argument("--heatmaps", help="Ouput heatmaps filename stem")
ap.add_argument("--tree", help="Output trees filename stem")
ap.add_argument("--deptree", help="Output dependency trees filename stem")
ap.add_argument("--staredness", help="Output staredness filename stem")
ap.add_argument("--not-aggreg", help="Not aggregated across layers")
args= ap.parse_args()

#load data
x = np.load(args.attentions)

# get number of tokens
size = x["encoder/layer_0/self_attention/add:0"].shape[2]
head_count = x["encoder/layer_0/self_attention/add:0"].shape[1]
print("Vector size:" + str(size))
print("Number of heads detected:" + str(head_count))

word_mixture = list()
word_mixture.append(np.identity(size))

if (args.weights):
    w = np.load(args.weights)

for layer in (range(6)):
    if (args.weights):
        head_weights = np.split(w["encoder/layer_" + str(layer) + "/self_attention/output_proj/kernel:0"], 16, axis=1)
    att = x["encoder/layer_" + str(layer) + "/self_attention/add:0"][0]
    layer_matrix = np.zeros((size, size))
    head_weight_sum = 0
    for head in (range(head_count)):
        head_weight = 1
        #head_weight = random.random()
        if (args.weights):
            head_weight = math.exp(np.sum(head_projs[head]) / 10 )
        #print("Weight of head" + str(head) + ": " + str(head_weight))
        head_weight_sum += head_weight
        matrix = att[head]
        #softmax
        deps = np.transpose(np.exp(np.transpose(matrix)) / np.sum(np.exp(np.transpose(matrix)), axis=0))
        layer_matrix = layer_matrix + deps * head_weight
    layer_matrix = layer_matrix / head_weight_sum
################ ONE HAEAD ONLY!!!!!!!
#    matrix = att[4]
#    deps = np.exp(matrix) / np.sum(np.exp(matrix), axis=0)
#    layer_matrix = deps
################ ONE HAEAD ONLY!!!!!!!

    if (args.not_aggreg):
        word_mixture.append(layer_matrix)
    else:
        word_mixture.append((word_mixture[layer] + layer_matrix) / 2)

#dependencies = np.zeros((size, size))
#for x in word_mixture[6]:
#    o = np.outer(x, x)
#    dependencies += o
#np.savez("dependencies.npz", deps)
#np.savez(args.mixtures, word_mixture)

labels_file = codecs.open(args.labels, "r", "utf-8")

sentences_src = list()
sent_src = list()

for line in labels_file:
    sentences_src.append(line.split())
    sent_src.append(line)

print("Number of labels:" + str(len(sentences_src[0])))
#if (len(sentences_src[0]) + 1 != size):
#    print("ERROR: Number of labels and size of attention matrix is not equal")

global_maxprob = np.zeros((size - 1, size - 1))

alignment = list()
if (args.alignment):
    alignment_file = open(args.alignment, "r")
    for line in alignment_file:
        ali = list()
        for a in line.split():
            ali.append(int(a))
        alignment.append(ali)
    print("Alignment size: " + str(len(alignment[0])))

word_count = alignment[0][-1] + 1
words = ['' for x in range(word_count)]
for i in range(len(alignment[0])):
    token = sentences_src[0][i]
    if (token[-1] == '_'):
        token = token[:-1]
    words[alignment[0][i]] += token

for i in range(len(words)):
    if (words[i] == '('):
        words[i] = '-LRB-'
    elif (words[i] == ')'):
        words[i] = '-RRB-'
    elif (words[i] == '['):
        words[i] = '-LSB-'
    elif (words[i] == ']'):
        words[i] = '-RSB-'
    elif (words[i] == '{'):
        words[i] = '-LCB-'
    elif (words[i] == '}'):
        words[i] = '-RCB-'

#for layer in range(0,7):
for layer in range(6,7): 
    # compute constituents probabilities
    maxprob = np.zeros((size - 1, size - 1))
    prob = np.zeros((word_count, word_count))
    for i in range(size - 1):
        for j in range(i, size - 1):
            ssum = 0
            # if the candidate bracket do not cross the alignment to PTB do the sum, else assign 0
            #print("ali:" + str(alignment[0][i]) + ' ' + str(alignment[0][j]))
            if (i == j or ((j == size - 2 or alignment[0][j] != alignment[0][j+1]) and (i == 0 or alignment[0][i] != alignment[0][i-1]))):
                for k in range(i, j + 1):
                    for l in range(i, j + 1):
                        ssum += word_mixture[layer][k][l]
                #maxprob[i][j] = ssum / (j - i + 1)**2
                maxprob[i][j] = ssum / (j - i + 1)
                #maxprob[i][j] = ssum
                prob[alignment[0][i]][alignment[0][j]] = maxprob[i][j]
            else:
                #print(str(i) + ' ' + str(j))
                maxprob[i][j] = 0
    # CKY on words (not on wordpieces)
    ctree = [[0 for i in range(word_count)] for j in range(word_count)]
    for i in range(word_count):
        ctree[i][i] = words[i]
    for span in range(1, word_count):
        for pos in range(0, word_count):
            if (pos + span < word_count):
                best_prob = -1
                best_variant = 0
                for variant in range(1, span + 1):
                    var_prob = prob[pos][pos + span - variant] * prob[pos + span - variant + 1][pos + span]
                    #var_prob = prob[pos][pos + span - variant] + prob[pos + span - variant + 1][pos + span]
                    if (best_prob < var_prob):
                        best_prob = var_prob
                        best_variant = variant
                #prob[pos][pos + span] *= best_prob
                #prob[pos][pos + span] += best_prob
                prob[pos][pos + span] *= 1
                ctree[pos][pos + span] = Tree('X', [ctree[pos][pos + span - best_variant], ctree[pos + span - best_variant + 1][pos + span]])
                if (prob[pos][pos + span - best_variant] + prob[pos + span - best_variant + 1][pos + span] * 0.6 < prob[pos][pos + span]):
                    #print("Flatten.")
                    children = list()
                    if isinstance(ctree[pos][pos + span - best_variant], str):
                        children.append(ctree[pos][pos + span - best_variant])
                    else:
                        for n, child in enumerate(ctree[pos][pos + span - best_variant]):
                            children.append(child)
                    if isinstance(ctree[pos + span - best_variant + 1][pos + span], str):
                        children.append(ctree[pos + span - best_variant + 1][pos + span])
                    else:
                        for n, child in enumerate(ctree[pos + span - best_variant + 1][pos + span]):
                            children.append(child)
                    ctree[pos][pos + span] = Tree('X', children)

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
    
    
    #print(maxprob)
    # CKY algorithm
    #ckyback = [[0 for x in range(size - 1)] for y in range(size - 1)]
    #ctree = [[0 for x in range(size - 1)] for y in range(size - 1)]
    #for i in range(size - 1):
    #    token = sentences_src[0][i]
    #    if (token[-1] == '_'):
    #        token = token[:-1]
    #    ctree[i][i] = token

    #for span in range(1, size - 1):
    #    for pos in range(0, size - 1):
    #        if (pos + span < size - 1):
    #            best_prob = -1
    #            best_variant = 0
    #            for variant in range(1, span + 1):
    #                print(str(pos) + ' ' + str(span) + ' ' + str(best_variant))
    #                var_prob = maxprob[pos][pos + span - variant] * maxprob[pos + span - variant + 1][pos + span]
    #                #print (str(pos)+','+str(pos+span)+' -> '+str(pos)+','+str(pos+span-variant)+' + '+str(pos+span-variant+1)+','+str(pos+span)+': '+str(var_prob)) 
    #                #var_prob = maxprob[pos][pos + span - variant] + maxprob[pos + span - variant][pos + span]
    #                if (best_prob < var_prob):
    #                    best_prob = var_prob
    #                    best_variant = variant
    #            #maxprob[pos][pos + span] *= best_prob
    #            maxprob[pos][pos + span] *= 1
    #            #maxprob[pos][pos + span] += best_prob
    #            ckyback[pos][pos + span] = best_variant
    #            print("B: " + str(pos) + ' ' + str(span) + ' ' + str(best_variant))
    #            ctree[pos][pos + span] = Tree('X', [ctree[pos][pos + span - best_variant], ctree[pos + span - best_variant + 1][pos + span]])
    if (layer == 6):
        file = open(args.tree, 'w')
        file.write(str(ctree[0][word_count - 1]) + '\n')
        file.close()
        print("Output written.")

    #print(maxprob)
    #print(ckyback)
    # CKY go back and create brackets
    #queue = [(0, size - 2)]
    #left_brackets = [''] * (size - 1)
    #right_brackets = [''] * (size - 1)
    #while (queue != []):
    #    (i, j) = queue.pop()
    #    if (j - i > 0):
    #        left_brackets[i] = left_brackets[i] + '('
    #        right_brackets[j] = right_brackets[j] + ')'
    #        if (j - i > 1):
    #            queue.append((i, j - ckyback[i][j]))
    #            queue.append((j - ckyback[i][j] + 1, j))
    #            #print (str(i) + ',' + str(j) + ' -> ' + str(i) + ',' + str(j - ckyback[i][j]) + ' + ' + str(j - ckyback[i][j] + 1) + ',' + str(j)) 
    #
    #for i in range(size - 1):
    #    print (left_brackets[i], end='')
    #    print (sentences_src[0][i], end='')
    #    print (right_brackets[i], end='')
    #print()

    #depth = 0
    #for i in range(size - 1):
    #    depth += len(left_brackets[i])
    #    if (i > 0):
    #        depth -= len(right_brackets[i - 1])
    #    if (len(left_brackets[i]) or len(right_brackets[i - 1]):
    #        for k in range(depth):
    #            print('\t', end='')
    #    print (left_brackets[i], end='')
    #    print (sentences_src[0][i], end='')
    #    print (right_brackets[i])

    if (layer < 7):
        heatmap(np.transpose(word_mixture[layer]), "", "", "", sentences_src[0], sentences_src[0])
        plt.savefig(args.heatmaps + str(layer) + '.png', dpi=300, format='png', bbox_inches='tight')

# Global CKY algorithm
#gtree = [[0 for x in range(size - 1)] for y in range(size - 1)]
#for i in range(size - 1):
#    gtree[i][i] = sentences_src[0][i]
#
#for span in range(1, size - 1):
#    for pos in range(0, size - 1):
#        if (pos + span < size - 1):
#            best_prob = 0
#            best_variant = 0
#            for variant in range(1, span + 1):
#                var_prob = global_maxprob[pos][pos + span - variant] * global_maxprob[pos + span - variant + 1][pos + span]
#                if (best_prob < var_prob):
#                    best_prob = var_prob
#                    best_variant = variant
#            gtree[pos][pos + span] = Tree('X', [gtree[pos][pos + span - best_variant], gtree[pos + span - best_variant + 1][pos + span]])
#file = open(args.tree + '-global', 'w')
#file.write('( ' + str(gtree[0][size - 2]) + ')')
#file.close()
#print("Global tree written.")


