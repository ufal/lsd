#!/usr/bin/env python3

import numpy as np
import codecs
import argparse
import matplotlib.pyplot as plt
from nltk import Tree
from matplotlib2tikz import save as tikz_save

def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels):
    '''
    Inspired by:
    - http://stackoverflow.com/a/16124677/395857 
    - http://stackoverflow.com/a/25074150/395857
    
    Copied form:
    https://stackoverflow.com/questions/20574257/constructing-a-co-occurrence-matrix-in-python-pandas
    '''

    # Plot it out
    fig, ax = plt.subplots(figsize=(3, 3))    
    c = ax.pcolor(AUC, edgecolors='k', linestyle= 'dashed', linewidths=0.2, cmap='pink', vmin=0.0, vmax=1.0)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(AUC.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(AUC.shape[1]) + 0.5, minor=False)

    # set tick labels
    xfont = {'family': 'serif', 'weight': 'normal', 'size': 9, 'rotation' : 'vertical'}
    yfont = {'family': 'serif', 'weight': 'normal', 'size': 9}
    
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
ap.add_argument("--en_labels", help="Labels separated by spaces")
ap.add_argument("--de_labels", help="Labels separated by spaces")
ap.add_argument("--fr_labels", help="Labels separated by spaces")
ap.add_argument("--es_labels", help="Labels separated by spaces")
ap.add_argument("--cs_labels", help="Labels separated by spaces")
ap.add_argument("--heatmaps", help="Ouput heatmaps filename stem")
ap.add_argument("--scheme", help="flat, serial, parallel, hierarchical")
args= ap.parse_args()

lang = ["es", "fr", "de", "en"]
lang2 = ["en", "de", "es", "fr"]
#lang2 = ["es", "fr", "de", "en"]

#load data
x = np.load(args.attentions)

# get number of tokens
src_size=dict()
for src_lang in ["en", "de", "fr", "es"]:
    src_size[src_lang] = x["encoder_" + src_lang + "/layer_0/self_attention/energies:0"].shape[2]
    print("Number of " + src_lang + " tokens:" + str(src_size[src_lang]))
trg_size = 0
if (args.scheme == 'flat'):
    trg_size = x["decoder/layer_0/encdec_attention/energies:0"].shape[2]
else:
    trg_size = x["decoder/layer_0/encdec_attention/enc_0/energies:0"].shape[2]
print("Number of target tokens:" + str(trg_size))

mixture = dict()
for src_lang in ["en", "de", "fr", "es"]:
    mixture[src_lang] = list()
    mixture[src_lang].append(np.identity(src_size[src_lang]))
    for layer in (range(4)):
        att = x["encoder_" + src_lang + "/layer_" + str(layer) + "/self_attention/energies:0"][0]
        layer_matrix = np.zeros((src_size[src_lang], src_size[src_lang]))
        for head in (range(8)):
            matrix = att[head]
            #softmax
            deps = np.transpose(np.exp(np.transpose(matrix)) / np.sum(np.exp(np.transpose(matrix)), axis=0))
            layer_matrix = layer_matrix + deps
        layer_matrix = layer_matrix / 8
        mixture[src_lang].append((mixture[src_lang][layer] + layer_matrix) / 2)

trg_mixture = list()
trg_direct = list()
trg_hier = np.zeros((6,4))

for layer in (range(6)):
    if (args.scheme == 'flat'):
        att = x["decoder/layer_" + str(layer) + "/encdec_attention/energies:0"][0]
        layer_matrix = np.zeros((trg_size, src_size["es"] + src_size["fr"] \
                                         + src_size["de"] + src_size["en"]))
        for head in (range(8)):
            #softmax
            deps = np.transpose(np.exp(np.transpose(att[head])) / np.sum(np.exp(np.transpose(att[head])), axis=0))
            layer_matrix += deps
        layer_matrix = layer_matrix / 8
        m = np.split(layer_matrix,[src_size[lang2[0]], \
                                   src_size[lang2[0]] + src_size[lang2[1]], \
                                   src_size[lang2[0]] + src_size[lang2[1]] + src_size[lang2[2]]],axis=1)
        trg_mixture.append(np.concatenate((np.matmul(m[2], mixture[lang2[2]][4]), \
                                           np.matmul(m[3], mixture[lang2[3]][4]), \
                                           np.matmul(m[1], mixture[lang2[1]][4]), \
                                           np.matmul(m[0], mixture[lang2[0]][4])),axis=1))
        #trg_mixture.append(layer_matrix)
        trg_direct.append(np.concatenate((np.matmul(m[2], mixture[lang2[2]][0]), \
                                          np.matmul(m[3], mixture[lang2[3]][0]), \
                                          np.matmul(m[1], mixture[lang2[1]][0]), \
                                          np.matmul(m[0], mixture[lang2[0]][0])),axis=1))
        #trg_direct.append(layer_matrix)
    else:
        att = list()
        lm = list()
        for l in (range(4)):
            att.append(x["decoder/layer_" + str(layer) + "/encdec_attention/enc_" + str(l) + "/energies:0"][0])
            if (args.scheme == 'serial' or args.scheme == 'parallel'):
                lm.append(np.zeros((trg_size, src_size[lang2[l]])))
            else:
                lm.append(np.zeros((trg_size, src_size[lang[l]])))
            for head in (range(8)):
                deps = np.transpose(np.exp(np.transpose(att[l][head])) / np.sum(np.exp(np.transpose(att[l][head])), axis=0))
                lm[l] += deps
            lm[l] = lm[l] / 8
        if (args.scheme == 'serial' or args.scheme == 'parallel'):
#            trg_mixture.append(np.concatenate((np.matmul(lm[0], mixture[lang2[0]][0]), \
#                                               np.matmul(lm[1], mixture[lang2[1]][0]), \
#                                               np.matmul(lm[2], mixture[lang2[2]][0]), \
#                                               np.matmul(lm[3], mixture[lang2[3]][0])), axis=1))
            trg_mixture.append(np.concatenate((np.matmul(lm[2], mixture[lang2[2]][4]), \
                                               np.matmul(lm[3], mixture[lang2[3]][4]), \
                                               np.matmul(lm[1], mixture[lang2[1]][4]), \
                                               np.matmul(lm[0], mixture[lang2[0]][4])), axis=1))
            trg_direct.append(np.concatenate((np.matmul(lm[2], mixture[lang2[2]][0]), \
                                             np.matmul(lm[3], mixture[lang2[3]][0]), \
                                             np.matmul(lm[1], mixture[lang2[1]][0]), \
                                             np.matmul(lm[0], mixture[lang2[0]][0])), axis=1))
        elif (args.scheme == 'hierarchical'):
            atth = x["decoder/layer_" + str(layer) + "/encdec_attention/enc_hier/energies:0"][0]
            print(x["decoder/layer_" + str(layer) + "/encdec_attention/enc_hier/energies:0"])
            print(x["decoder/layer_" + str(layer) + "/encdec_attention/enc_hier/energies:0"].shape)
            atth = np.squeeze(atth, axis=1)
            lmh = [0, 0, 0, 0]
            for head in (range(8)):
                #depsh = np.transpose(np.exp(np.transpose(atth[head])) / np.sum(np.exp(np.transpose(atth[head])), axis=0))
                depsh = np.exp(atth[head]) / np.sum(np.exp(atth[head]))
                lmh += depsh
            lmh = lmh / 8
            print("Distribution across languages: " + str(lmh))
            trg_mixture.append(np.concatenate((np.multiply(np.matmul(lm[0], mixture[lang[0]][4]), lmh[0]), \
                                               np.multiply(np.matmul(lm[1], mixture[lang[1]][4]), lmh[1]), \
                                               np.multiply(np.matmul(lm[2], mixture[lang[2]][4]), lmh[2]), \
                                               np.multiply(np.matmul(lm[3], mixture[lang[3]][4]), lmh[3])), axis=1))
            trg_direct.append(np.concatenate((np.multiply(np.matmul(lm[0], mixture[lang[0]][0]), lmh[0]), \
                                             np.multiply(np.matmul(lm[1], mixture[lang[1]][0]), lmh[1]), \
                                             np.multiply(np.matmul(lm[2], mixture[lang[2]][0]), lmh[2]), \
                                             np.multiply(np.matmul(lm[3], mixture[lang[3]][0]), lmh[3])), axis=1))
            trg_hier[layer] = lmh


en_labels = list()
en_labels_file = codecs.open(args.en_labels, "r", "utf-8")
for line in en_labels_file:
    en_labels.append(line.split())

de_labels = list()
de_labels_file = codecs.open(args.de_labels, "r", "utf-8")
for line in de_labels_file:
    de_labels.append(line.split())

fr_labels = list()
fr_labels_file = codecs.open(args.fr_labels, "r", "utf-8")
for line in fr_labels_file:
    fr_labels.append(line.split())

es_labels = list()
es_labels_file = codecs.open(args.es_labels, "r", "utf-8")
for line in es_labels_file:
    es_labels.append(line.split())

cs_labels = list()
cs_labels_file = codecs.open(args.cs_labels, "r", "utf-8")
for line in cs_labels_file:
    cs_labels.append(line.split())

print("ES labels: " + str(len(es_labels[0])))
print("DE labels: " + str(len(de_labels[0])))
print("FR labels: " + str(len(fr_labels[0])))
print("EN labels: " + str(len(en_labels[0])))
print("CS labels: " + str(len(cs_labels[0])))


#for layer in range(6):
#    heatmap(trg_direct[layer], "", "", "", es_labels[0] + fr_labels[0] + de_labels[0] + en_labels[0], cs_labels[0])
#    plt.savefig(args.heatmaps + '-direct' + str(layer) + '.pdf', dpi=400, format='pdf', bbox_inches='tight')
#    tikz_save(args.heatmaps + '-direct' + str(layer) + '.tex')
#    heatmap(trg_mixture[layer], "", "", "", es_labels[0] + fr_labels[0] + de_labels[0] + en_labels[0], cs_labels[0])
#    plt.savefig(args.heatmaps + str(layer) + '.pdf', dpi=400, format='pdf', bbox_inches='tight')
#    tikz_save(args.heatmaps + str(layer) + '.tex')
if(args.scheme == 'hierarchical'):
    heatmap(trg_hier, "", "", "", ["es", "fr", "de", "en"], ["layer 0", "layer 1", "layer 2", "layer 3", "layer 4", "layer 5"])
    plt.savefig(args.heatmaps + 'H.pdf', dpi=400, format='pdf', bbox_inches='tight')
    tikz_save(args.heatmaps + 'H.tex')





