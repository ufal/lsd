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

for i, t in enumerate(trees):
    tree = Tree.fromstring(t)
    # remove punctuation
    for sub in tree.subtrees():
        remove = list()
        for n, child in enumerate(sub):
            if isinstance(child, str):
                if (re.match(r'^(\.|,|\?|!|;|:|\'|\'\'|`|``|&apos;|&quot;|-[LR][RSC]B-|-|--)$', child)):
                    remove.append(n)
                    #del sub[n]
        for n in sorted(remove, reverse=True):
            del sub[n]
    #sys.stderr.write(str(len(tree.leaves())) + ' ')
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

    #sys.stderr.write(" ".join(tree.leaves()) + '\n')
    # printout only if number of tokens is at most 40
    if (len(tree.leaves()) <= 40):
        print(str(tree))
