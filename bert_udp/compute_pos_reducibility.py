#!/usr/bin/env python3

import sys
import re

from collections import defaultdict

# both
ID = 0
# conll
POS = 3
PARENT = 6
# score
SCORE = 5

# compute INVERSE reducibility

def readconllu(filename):
    with open(filename, 'r') as infile:
        leaves = defaultdict(int)
        nonleaves = defaultdict(int)
        poses = list()
        haschildren = defaultdict(bool)
        for line in infile:
            if line.startswith('#'):
                # comment
                pass
            elif line == '\n':
                # end of sentence
                for item in range(len(poses)):
                    pos = poses[item]
                    if haschildren[item]:
                        nonleaves[pos] += 1
                    else:
                        leaves[pos] += 1
                poses = list()
                haschildren = defaultdict(bool)
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    # 1-based -> 0-based
                    item_id = int(item_id)-1
                    parent_id = int(items[PARENT])-1
                    poses.append(items[POS])
                    haschildren[parent_id] = True
        poses = set()
        poses.update(leaves.keys())
        poses.update(nonleaves.keys())
        for pos in poses:
            if pos not in leaves:
                red = 1
            elif pos not in nonleaves:
                red = 0.001
            else:
                red = nonleaves[pos]/(nonleaves[pos] + leaves[pos])
            print(pos, red, sep="\t")


if len(sys.argv) != 2:
    exit('Usage: ' + sys.argv[0] + ' file.conllu')
    
readconllu(sys.argv[1])






