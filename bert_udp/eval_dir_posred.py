#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
POS = 3
PARENT = 6
# score
S_POS = 0
SCORE = 1

def readconllu(filename):
    result = list()
    cur_sent_poses = list()
    cur_sent_parents = list()
    with open(filename, 'r') as infile:
        for line in infile:
            if line.startswith('#'):
                # comment
                pass
            elif line == '\n':
                # end of sentence
                length = len(cur_sent_parents)
                for child, parent in zip(range(length), cur_sent_parents):
                    if parent != -1:  # skip root
                        edge = (cur_sent_poses[child], cur_sent_poses[parent])
                        result.append(edge)
                cur_sent_poses = list()
                cur_sent_parents = list()
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    # 1-based -> 0-based
                    parent_id = int(items[PARENT]) - 1
                    pos = items[POS]
                    cur_sent_poses.append(pos)
                    cur_sent_parents.append(parent_id)
    return result


def readscores(filename):
    result = dict()
    with open(filename, 'r') as infile:
        for line in infile:
            items = line.split('\t')
            pos = items[S_POS]
            score = float(items[SCORE])
            result[pos] = score
    return result

if len(sys.argv) != 3:
    exit('Usage: ' + sys.argv[0] + ' file.conllu file.pos_scores')
    
conllu = readconllu(sys.argv[1])
scores = readscores(sys.argv[2])

correct = 0
total = 0
for child_pos, parent_pos in conllu:
        # negative reducibility: lower is more reducible
        if scores[child_pos] < scores[parent_pos]:
            correct += 1
        total += 1

print(str(correct/total))

