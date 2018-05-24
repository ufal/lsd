#!/usr/bin/env python3

from nltk.corpus import ptb
import nltk.tree

tree_file = open("trees", 'w')
word_file = open("words", 'w')

trees = ptb.parsed_sents('wsj/22/wsj_2200.mrg')
words = list()
tags = list()
for i in range(len(trees)):
    # remove traces and other empty nodes
    for sub in trees[i].subtrees():
        for n, child in enumerate(sub):
            if isinstance(child, str):
                continue
            if (all(leaf.startswith("*") for leaf in child.leaves()) or child.label() == '-NONE-'):
                del sub[n]
    # extract list of POS tags and remove POS tags from the trees
    sent_tags = list()
    for sub in trees[i].subtrees():
        for n, child in enumerate(sub):
            if isinstance(child, str):
                continue
            leaves = child.leaves()
            # delete all brackets containing only one token
            if (len(leaves) == 1):
                sent_tags.append(child.label())
                sub[n] = leaves[0]
    tags.append(sent_tags)
    tree_file.write(str(trees[i]) + '\n')
    # save tokens
    words.append(trees[i].leaves())
    word_file.write(' '.join(trees[i].leaves()) + '\n')

tree_file.close
word_file.close




