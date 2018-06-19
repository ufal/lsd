#!/usr/bin/env python3

from nltk.tree import Tree
import sys
import math

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

count = dict()

for t in trees:
    tree = Tree.fromstring(t)
    for sub in tree.subtrees():
        constituent = " ".join(sub.leaves())
        if constituent not in count:
            count[constituent] = 1
        else:
            count[constituent] += 1

score = 0
total = 0
alpha = 0.1
sum_alpha = len(count) * alpha

for constituent in count:
    for i in range(count[constituent]):
        score += math.log((alpha + i) / (sum_alpha + total))
        total += 1

print(score)


        







