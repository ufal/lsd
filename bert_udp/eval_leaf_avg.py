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

def readscores(filename):
    correct = 0
    total = 0
    sent_reds = list()
    sent_isleaf = list()
    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                # comment
                pass
            elif line == '\n':
                # end of sentence: evaluate
                avg = sum(sent_reds) / len(sent_reds)
                #print(avg)
                for red, isleaf in zip(sent_reds, sent_isleaf):
                    total += 1
                    pred_leaf = red < avg*1.2
                    if pred_leaf == isleaf:
                        correct += 1
                    #print(isleaf, pred_leaf, red)
                sent_reds = list()
                sent_isleaf = list()
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    sent_reds.append(float(items[SCORE]))
                    sent_isleaf.append(items[NONE] != '<none>')

    return correct/total

if len(sys.argv) == 2:
    result = readscores(sys.argv[1])
else:
    exit('Usage: ' + sys.argv[0] + ' test2.scores')


print(result)

