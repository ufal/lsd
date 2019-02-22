#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
PARENT = 6
# score
SCORE = 5

def readconllu(filename):
    result = list()
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
                    # 1-based
                    item_id = int(item_id)
                    parent_id = int(items[PARENT])
                    if parent_id == 0:
                        result.append(item_id)
    return result

def readscores(filename):
    result = list()
    cur_sent = dict()
    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                # comment
                pass
            elif line == '\n':
                # end of sentence
                result.append(cur_sent)
                cur_sent = dict()
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    # 0-based -> 1-based
                    item_id = int(item_id) + 1
                    cur_sent[item_id] = float(items[SCORE])
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' file.conllu file.scores')
    
conllu = readconllu(sys.argv[1])
scores = readscores(sys.argv[2])

if (len(conllu) != len(scores)):
    exit("Different number of sentences: " + str(len(conllu)) + " != " + str(len(scores)))

correct = 0
total = 0
for sent_root, sent_scores in zip(conllu, scores):
    # negative reducibility: lower is more reducible
    least_reducible = max(sent_scores, key=sent_scores.get)
    if least_reducible == sent_root:
        correct += 1
    total += 1

print(str(correct/total))

