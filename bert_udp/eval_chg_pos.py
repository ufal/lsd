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
                    # 1-based -> 0-based
                    item_id = int(item_id) - 1
                    parent_id = int(items[PARENT]) - 1
                    cur_sent[item_id] = items[POS]
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
                    scores_temp = items[SCORES].split()
                    scores = scores_temp[:item_id]
                    scores.append('0')
                    scores.extend(scores_temp[item_id:])
                    scores = [float(x) for x in scores]
                    # 0-based
                    for child_id in range(len(scores)):
                        #cur_sent[(item_id, parent_id)] = scores[parent_id]
                        cur_sent[(child_id, item_id)] = scores[child_id]
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' file.conllu file.scores')
    
conllu = readconllu(sys.argv[1])
scores = readscores(sys.argv[2])

if (len(conllu) != len(scores)):
    exit("Different number of sentences: " + str(len(conllu)) + " != " + str(len(scores)))

poses = defaultdict(int)
total = 0
for sent_conllu, sent_scores in zip(conllu, scores):
    length = len(sent_conllu)
    for child in range(length):  # child is the changed node
        removed_node = -1
        mc_score = -1
        for node in range(length):
            score = sent_scores[(child,node)]
            #score = sent_scores[(node,child)]
            if score > mc_score:
                removed_node = node
                mc_score = score

        # START alwqays take neighbor
        removed_node = child - 1
        if removed_node == -1:
            continue
        # END alwqays take neighbor
        
        # START only longer deps
        #dist = abs(removed_node - child)
        #if dist == 1:
        #    continue
        # END only longer deps
        total += 1
        pos = sent_conllu[removed_node]
        poses[pos] += 1

for pos in sorted(poses):
    print(pos, poses[pos]/total, sep='\t')

