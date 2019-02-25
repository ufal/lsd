#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
POS = 3
PARENT = 6
DEPREL = 7
# score
SCORE = 5

THRESH = 4.7

POSES = {'NOUN', 'PROPN', 'VERB'}

def readposes(filename):
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
    result.append(None)
    return result

def readconllu(filename, scores, poses):
    sent_id = 0
    sent_scores = scores[sent_id]
    sent_poses = poses[sent_id]
    length = len(sent_scores)
    sent_root = -1
    with open(filename, 'r') as infile:
        for line in infile:
            line = line.rstrip()
            if line.startswith('#'):
                # comment
                print(line)
            elif line == '':
                # end of sentence
                print(line)
                sent_id += 1
                sent_scores = scores[sent_id]
                sent_poses = poses[sent_id]
                length = len(sent_scores)
                sent_root = -1
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    # 1-based -> 0-based
                    item_id = int(item_id) - 1
                    # 0-based
                    parent = -1
                    for potential_parent in range(item_id+1, length):
                        if sent_poses[potential_parent] in POSES:
                            parent = potential_parent
                            break
                    if parent == -1:
                        parent = sent_root
                    if parent == -1:
                        sent_root = item_id
                    # 0-based > 1-based
                    items[PARENT] = parent + 1
                    #items[DEPREL] = str(round(sent_scores[item_id], 2))
                print(*items, sep="\t")
    return

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
                    cur_sent.append(float(items[SCORE]))
    result.append('')
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' test2.input test2.scores')
    
scores = readscores(sys.argv[2])
poses = readposes(sys.argv[1])
readconllu(sys.argv[1], scores, poses)


