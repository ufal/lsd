#!/usr/bin/env python3

import numpy as np
import codecs
import argparse
import matplotlib.pyplot as plt
from nltk import Tree

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
    xfont = {'family': 'serif', 'weight': 'normal', 'size': 6, 'rotation' : 'vertical'}
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
ap.add_argument("--src_labels", help="Labels separated by spaces")
ap.add_argument("--mt_labels", help="Labels separated by spaces")
ap.add_argument("--pe_labels", help="Labels separated by spaces")
ap.add_argument("--heatmaps", help="Ouput heatmaps filename stem")
ap.add_argument("--scheme", help="flat, serial, parallel, hierarchical")
args= ap.parse_args()

#load data
x = np.load(args.attentions)
# get number of tokens
src_size = x["source_encoder/layer_0/self_attention/energies:0"].shape[2]
print("Number of SRC tokens:" + str(src_size))
mt_size = x["mt_encoder/layer_0/self_attention/energies:0"].shape[2]
print("Number of MT tokens:" + str(mt_size))
pe_size = 0
if (args.scheme == 'flat'):
    pe_size = x["decoder/layer_0/encdec_attention/energies:0"].shape[2]
else:
    pe_size = x["decoder/layer_0/encdec_attention/enc_0/energies:0"].shape[2]
print("Number of PE tokens:" + str(pe_size))

src_mixture = list()
src_mixture.append(np.identity(src_size))

for layer in (range(6)):
    att = x["source_encoder/layer_" + str(layer) + "/self_attention/energies:0"][0]
    layer_matrix = np.zeros((src_size, src_size))
    for head in (range(16)):
        matrix = att[head]
        #softmax
        deps = np.exp(matrix) / np.sum(np.exp(matrix), axis=0)
        layer_matrix = layer_matrix + deps
    layer_matrix = layer_matrix / 16
    src_mixture.append((src_mixture[layer] + layer_matrix) / 2)

mt_mixture = list()
mt_mixture.append(np.identity(mt_size))

for layer in (range(6)):
    att = x["mt_encoder/layer_" + str(layer) + "/self_attention/energies:0"][0]
    layer_matrix = np.zeros((mt_size, mt_size))
    for head in (range(16)):
        matrix = att[head]
        #softmax
        deps = np.exp(matrix) / np.sum(np.exp(matrix), axis=0)
        layer_matrix = layer_matrix + deps
    layer_matrix = layer_matrix / 16
    mt_mixture.append((mt_mixture[layer] + layer_matrix) / 2)

#print(src_mixture[6].shape)
#print(mt_mixture[6].shape)

pe_mixture = list()

for layer in (range(6)):
    if (args.scheme == 'flat'):
        att = x["decoder/layer_" + str(layer) + "/encdec_attention/energies:0"][0]
        layer_matrix = np.zeros((pe_size, src_size + mt_size))
        for head in (range(16)):
            #softmax
            deps = np.exp(att[head]) / np.sum(np.exp(att[head]), axis=0)
            layer_matrix += deps
        layer_matrix = layer_matrix / 16
        m = np.split(layer_matrix,[src_size],axis=1)
        pe_mixture.append(np.concatenate((np.matmul(m[0],src_mixture[6]),np.matmul(m[1], mt_mixture[6])),axis=1))
    else:
        att0 = x["decoder/layer_" + str(layer) + "/encdec_attention/enc_0/energies:0"][0]
        att1 = x["decoder/layer_" + str(layer) + "/encdec_attention/enc_1/energies:0"][0]
        lm0 = np.zeros((pe_size, src_size))
        lm1 = np.zeros((pe_size, mt_size))
        for head in (range(16)):
            deps0 = np.exp(att0[head]) / np.sum(np.exp(att0[head]), axis=0)
            deps1 = np.exp(att1[head]) / np.sum(np.exp(att1[head]), axis=0)
            lm0 += deps0
            lm1 += deps1
        lm0 = lm0 / 16
        lm1 = lm1 / 16
        if (args.scheme == 'serial'):
            pe_mixture.append(np.concatenate((np.matmul(lm0, src_mixture[6]), np.matmul(lm1, mt_mixture[6])), axis=1))
        elif (args.scheme == 'parallel'):
            pe_mixture.append(np.concatenate((np.matmul(lm0, src_mixture[6]), np.matmul(lm1, mt_mixture[6])), axis=1))
        elif (args.scheme == 'hierarchical'):
            atth = x["decoder/layer_" + str(layer) + "/encdec_attention/enc_hier/energies:0"][0]
            lmh = np.zeros((pe_size, 2))
            for head in (range(4)):
                depsh = np.exp(atth[head]) / np.sum(np.exp(atth[head]), axis=0)
                lmh += depsh
            lmh = lmh / 4
            #lm0 = np.matmul(lm0, src_mixture[6])
            #lm1 = np.matmul(lm1, mt_mixture[6])
            pe_mixture.append(np.concatenate((np.multiply(np.matmul(lm0, src_mixture[6]), lmh[:,[0]]), np.multiply(np.matmul(lm1, mt_mixture[6]),lmh[:,[1]])), axis=1))
            #print(lm0.shape)
            #print(lm1.shape)


src_labels = list()
src_labels_file = codecs.open(args.src_labels, "r", "utf-8")
for line in src_labels_file:
    src_labels.append(line.split())

mt_labels = list()
mt_labels_file = codecs.open(args.mt_labels, "r", "utf-8")
for line in mt_labels_file:
    mt_labels.append(line.split())

pe_labels = list()
pe_labels_file = codecs.open(args.pe_labels, "r", "utf-8")
for line in pe_labels_file:
    pe_labels.append(line.split())

for layer in range(6):
    heatmap(pe_mixture[layer], "", "", "", src_labels[0] + mt_labels[0], pe_labels[0])
    plt.savefig(args.heatmaps + str(layer) + '.png', dpi=400, format='png', bbox_inches='tight')


