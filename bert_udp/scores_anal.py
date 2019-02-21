#!/usr/bin/env python3

import sys
import re
from collections import defaultdict

# both
ID = 0
# conll
FORM = 1
POS = 3
PARENT = 6
# score
NONE = 3
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
                    scores.append('0')
                    scores.extend(scores_temp[item_id:])
                    scores = [float(x) for x in scores]
                    cur_sent.append(scores)
    return result

def readnone(filename):
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
                    isnone = ('none' if items[NONE] == '<none>' else 'leaf')
                    cur_sent.append(isnone)
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' file.conllu file.scores')
    
conllu = readconllu(sys.argv[1])
nones  = readnone(sys.argv[2])
scores = readscores(sys.argv[2])

if (len(conllu) != len(scores)):
    exit("Different number of sentences: " + str(len(conllu)) + " != " + str(len(scores)))

sums = defaultdict(float)
counts = defaultdict(int)

for sent_poses, sent_scores, sent_nones in zip(conllu, scores, nones):
    poses = sent_poses[0]
    for line in sent_scores:
        for score, pos, none in zip(line, poses, sent_nones):
            posn = pos + str(none)
            sums[posn] += score
            counts[posn] += 1

avgs = dict()
for pos in sums.keys():
    avgs[pos] = sums[pos]/counts[pos]

poses = sorted(avgs.keys(), key=avgs.get)
for pos in poses:
    if counts[pos] > 100:
        ppos = ('    ' + pos)[-9:]
        print(ppos, counts[pos], avgs[pos], sep="\t")


