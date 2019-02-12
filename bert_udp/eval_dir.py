#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
PARENT = 6
# score
SCORE = 2

def readconllu(filename):
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
                if items[ID].isdigit():
                    cur_sent[items[ID]] = items[PARENT]
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
                if items[ID].isdigit():
                    cur_sent[items[ID]] = float(items[SCORE])
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' file.conllu file.scores')
    
conllu = readconllu(sys.argv[1])
scores = readscores(sys.argv[2])

if (len(conllu) != len(scores)):
    exit("Different number of sentences: " + str(len(conllu)) + " != " + str(len(scores)))

correct = 0
total = 0
for sent_conllu, sent_scores in zip(conllu, scores):
    if len(sent_conllu) != len(sent_scores):
        exit("Different number of words: " + str(len(sent_conllu)) + " != " + str(len(sent_scores)))
    for child, parent in sent_conllu.items():
        # negative reducibility: lower is more reducible
        red_correct = sent_scores[child]
        red_reverse = sent_scores[parent]
        if red_correct < red_reverse:
            correct += 1
        total += 1

print(str(correct/total))

