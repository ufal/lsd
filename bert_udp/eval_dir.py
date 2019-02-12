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
else:
    conllu = readconllu(sys.argv[1])
    scores = readscores(sys.argv[2])

    if (len(conllu) != len(scores)):
        print("Different number of sentences: " + str(len(conllu)) + " != " + str(len(scores)))
        exit()

    correct = 0
    for i in range(len(gp)):
        if gp[i] == pp[i]:
            correct += 1

    print(str(correct/len(pp)))


