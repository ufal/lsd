#!/usr/bin/env python3

import sys
import re

# both
ID = 0
# conll
PARENT = 6
# score
SCORE = 5

def readconllu(filename):
    result = list()
    with open(filename, 'r') as infile:
        for line in infile:
            line = line.rstrip()
            if line.startswith('#'):
                # comment
                pass
            elif line == '':
                # end of sentence
                result[-1][PARENT] = '0'
                result.append([''])
            else:
                items = line.split('\t')
                item_id = items[ID]
                if item_id.isdigit():
                    item_id = int(item_id)
                    items[PARENT] = str(item_id + 1)
                    result.append(items)
    return result


if len(sys.argv) != 2:
    exit('Usage: ' + sys.argv[0] + ' file.conllu')
    
result = readconllu(sys.argv[1])
for line in ['\t'.join(items) for items in result]:
    print(line)

