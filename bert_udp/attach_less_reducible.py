#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
PARENT = 6
# score
SCORE = 5

def readconllu(filename, scores):
    sent_id = 0
    sent_scores = scores[sent_id]
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
                length = len(sent_scores)
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    # 1-based -> 0-based
                    item_id = int(item_id) - 1
                    # 0-based
                    right_parent = -1
                    for potential_parent in range(item_id, length):
                        if sent_scores[item_id] < sent_scores[potential_parent]:
                            right_parent = potential_parent
                            break
                    left_parent = -1
                    for potential_parent in range(item_id)[::-1]:
                        if sent_scores[item_id] < sent_scores[potential_parent]:
                            left_parent = potential_parent
                            break
                    parent = -1
                    if right_parent != -1 and left_parent != -1:
                        # choose the less reducible
                        if sent_scores[left_parent] > sent_scores[right_parent]: 
                            parent = left_parent
                        else:
                            parent = right_parent
                    else:
                        # choose the one that is not -1
                        parent = max(left_parent, right_parent)
                    # if it stays -1, it becomes the root
                    # 0-based > 1-based
                    items[PARENT] = parent + 1
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
readconllu(sys.argv[1], scores)


