#!/usr/bin/env python3

from nltk.tree import Tree
import sys
import re

trees = list()
tree = ''
for line in sys.stdin:
    if (line[0] == '('):
        if (tree != ''):
            trees.append(tree)
            tree = ''
    tree += line
if (tree != ''):
    trees.append(tree)

for t in trees:
    tree = Tree.fromstring(t)
    # remove punctuation
    for sub in tree.subtrees():
        for n, child in enumerate(sub):
            if isinstance(child, str):
                if (re.match(r'^(\.|,|\?|!|;|:|\'|&amp;|&quot;)$', child)):
                    del sub[n]
    # remove brackets with one item
    for sub in tree.subtrees():
        for n, child in enumerate(sub):
            if isinstance(child, str):
                continue
            if (len(child) == 1):
                sub[n] = child[0]
    strtree = str(tree)
    # remove the tompost brackets with one item
    for sub in tree.subtrees():
        if (len(sub.leaves()) == len(tree.leaves())):
            tree = sub

    # printout only if number of tokens is at most 40
    if (len(tree.leaves()) <= 40):
        print(str(tree))
