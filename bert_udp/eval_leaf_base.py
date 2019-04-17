#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
PARENT = 6
# score
NONE = 3
POS = 2
SCORE = 5

def readscores(filename, thresh=4.5):
    correct = 0
    total = 0
    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                # comment
                pass
            elif line == '\n':
                # end of sentence
                pass
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    leaf_red = True
                    leaf_gold = items[NONE] != '<none>'
                    total += 1
                    if leaf_gold == leaf_red:
                        correct += 1

    return correct/total

if len(sys.argv) == 2:
    result = readscores(sys.argv[1])
elif len(sys.argv) == 3:
    result = readscores(sys.argv[1], float(sys.argv[2]))
else:
    exit('Usage: ' + sys.argv[0] + ' test2.scores [thresh]')


print(result)

