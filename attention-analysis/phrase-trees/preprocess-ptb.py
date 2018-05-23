#!/usr/bin/env python3

from nltk.corpus import ptb
import nltk.tree

trees = ptb.parsed_sents('wsj/22/wsj_2200.mrg')
words = list()
tags = list()
for i in range(len(trees)):
    print(trees[i])
    # remove traces and other empty nodes
    for sub in trees[i].subtrees():
        for n, child in enumerate(sub):
            if isinstance(child, str):
                continue
            if all(leaf.startswith("*") for leaf in child.leaves()):
                del sub[n]  # Delete this child
    #print(trees[i])
    # save tokens
    words.append(trees[i].leaves())
    #print(words[-1])
    # extract list of POS tags and remove POS tags from the trees
    for sub in trees[i].subtrees():
        for n, child in enumerate(sub):
            if isinstance(child, str):
                continue
            leaves = child.leaves()
            if (len(leaves) == 1):
                sub[n] = leaves[0]
    print(trees[i])
