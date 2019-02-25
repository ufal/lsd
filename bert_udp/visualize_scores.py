#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
FORM = 1
PARENT = 6
# score
SCORE = 5

def readconllu(filename):
    result = list()
    cur_sent = list()
    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                # comment
                pass
            elif line == '\n':
                # end of sentence
                result.append(cur_sent)
                cur_sent = list()
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    cur_sent.append(items[FORM])
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
                    item_id = int(item_id)
                    cur_sent[item_id] = float(items[SCORE])
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' test2.input test2.scores')
    
conllu = readconllu(sys.argv[1])
scores = readscores(sys.argv[2])

if (len(conllu) != len(scores)):
    exit("Different number of sentences: " + str(len(conllu)) + " != " + str(len(scores)))

for sent_forms, sent_scores in zip(conllu, scores):
    ids_sorted = sorted(sent_scores, key=sent_scores.get, reverse=True)
    print(*sent_forms)
    for tok_id in ids_sorted:
        print(('    ' * tok_id),
                sent_forms[tok_id],
                #'({4.2f})'.format(sent_scores[tok_id])
                '({:4.2f})'.format(sent_scores[tok_id])
                )
    print()

