#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
FORM = 1
POS = 3
PARENT = 6
# score
SCORE = 5
SCORES = 6

def readconllu(filename):
    result = list()
    poses = list()
    forms = list()
    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                # comment
                pass
            elif line == '\n':
                # end of sentence
                result.append((poses, forms))
                poses = list()
                forms = list()
            else:
                items = line.split('\t')
                if items[ID].isdigit():
                    poses.append(items[POS])
                    forms.append(items[FORM][:6])
    return result

def readscores(filename):
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
                    item_id = int(item_id)
                    scores_temp = items[SCORES].split()
                    scores = scores_temp[:item_id]
                    scores.append('-1')
                    scores.extend(scores_temp[item_id:])
                    scores = ['{: 6.2f}'.format(float(x)) if x != '-1' else '' for x in scores]
                    cur_sent.append(scores)
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' file.conllu file.scores')
    
conllu = readconllu(sys.argv[1])
scores = readscores(sys.argv[2])

if (len(conllu) != len(scores)):
    exit("Different number of sentences: " + str(len(conllu)) + " != " + str(len(scores)))

for sent_poses, sent_scores in zip(conllu, scores):
    print(*(sent_poses[0]), sep='\t')
    print(*(sent_poses[1]), sep='\t')
    for line in sent_scores:
        print(*line, sep='\t')
    print()


