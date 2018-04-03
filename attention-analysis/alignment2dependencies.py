#!/usr/bin/env python3

import numpy as np
import codecs
import pylab
from operator import itemgetter
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
import networkx as nx

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
    c = ax.pcolor(AUC, edgecolors='k', linestyle= 'dashed', linewidths=0.2, cmap='RdBu', vmin=0.0, vmax=1.0)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(AUC.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(AUC.shape[1]) + 0.5, minor=False)

    # set tick labels
    #ax.set_xticklabels(np.arange(1,AUC.shape[1]+1), minor=False)
    ax.set_xticklabels(xticklabels, minor=False)
    ax.set_yticklabels(yticklabels, minor=False)

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

f_tgt = codecs.open("newstest2017.cs.translated", "r", "utf-8")
f_src = codecs.open("newstest2017.en.bpe", "r", "utf-8")

sentences_src = list()
sentences_tgt = list()
sent_src = list()
sent_tgt = list()

for line in f_src:
    sentences_src.append(line.split())
    sent_src.append(line)

for line in f_tgt:
    sentences_tgt.append(line.split())
    sent_tgt.append(line)

show = 30
s = 0
im = 0
for x in np.load('alignment.txt.out.npy'):
    x = np.transpose(x)
    size = x.shape[1]
    # compute dependency weights from attention matrices 
    deps = np.zeros((size,size))
    for y in x:
        o = np.outer(y, y)
        deps += o
    for i in range(size):
        deps[i][i] = 0.0
    # show only first <show> examples
    if (s < show):
        plt.figure(s)
        # build graph
        G = nx.Graph()
        for i in range(size):
            for j in range(size):
                if (i < j):
                    G.add_edges_from([(i, j, {'myweight':deps[i][j]})])
        # spring layout
        pos = nx.spring_layout(G, iterations=500, weight='myweight', k=0.05)
        # draw nodes
        nx.draw_networkx_nodes(G, pos, alpha=0.5, )
        # draw labels
        labels={}
        for i in range(size - 1):
            labels[i] = sentences_src[s][i]
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        # compute maximum spanning tree
        mst = deps
        for i in range(size):
            for j in range(size):
                if (i < j):
                    mst[i][j] = 0.0
            mst[i][size-1] = 0.0
            mst[size-1][i] = 0.0
        csr = csr_matrix(-1 * mst)
        Tcsr = minimum_spanning_tree(csr)
        mst = -1 * Tcsr.toarray()
        # list of edges in the spanning tree
        mst_edges = list()
        for i in range(size):
            for j in range(size):
                if (mst[i][j] != 0.0):
                    mst_edges.append((i,j))
        # draw the maximum spanning tree
        nx.draw_networkx_edges(G, pos, edgelist=mst_edges)
        plt.savefig('tree'+str(s)+'.png', dpi=300, format='png', bbox_inches='tight')
        # print MST dependency tree to STDOUT
        print('\\begin{dependency}')
        print('  \\begin{deptext}')
        print('    ', end='')
        for i in range(size - 1):
            print(sentences_src[s][i], end=' ')
            if (i != size - 2):
                print('\&', end=' ')
            else:
                print('\\')
        print('  \end{deptext}')
        for i in range(size - 1):
            for j in range(size - 1):
                if (mst[i][j] != 0):
                    print('  \depedge{' + str(i + 1) + '}{' + str(j + 1) + '}{}')
        print('\end{dependency}')
        # show heatmaps
        #heatmap(deps, "", "", "", sentences_src[s], sentences_src[s])
        #plt.savefig('dep.png', dpi=300, format='png', bbox_inches='tight')
        #heatmap(mst, "", "", "", sentences_src[s], sentences_src[s])
        #plt.savefig('mst.png', dpi=300, format='png', bbox_inches='tight')
        #heatmap(x, "", "", "", sentences_src[s], sentences_tgt[s])
        #plt.savefig('ali.png', dpi=300, format='png', bbox_inches='tight')
    s += 1
