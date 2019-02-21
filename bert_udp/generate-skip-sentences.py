#!/usr/bin/python3

import sys
import re

def generate(tokens):
    sentence = " ".join(tokens)
    print('#sentence: ' + sentence)
    
    c = 0        
    for i in range(len(tokens)):
        print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
        c += 1
    print()

    for k in range(len(tokens)):
        for l in range(len(tokens) - k):
            if k == 0 and l == len(tokens) - 1:
                continue
            print('#skipped: ' + " ".join(str(x) for x in range(k, k + l + 1))) 
            c = 0
            for i in range(len(tokens)):
                if i < k or i > k + l:
                    print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
                    c += 1
            print()

tokens = list() 
tags = list()
parents = list()
deprels = list()

for line in sys.stdin:
    line = line.rstrip('\n')
    if re.match('^#', line):
        tokens = []
        tags = []
        parents = []
        deprels = []
    elif re.match('^[0-9]', line):
        items = line.split('\t')
        tokens.append(items[1])
        tags.append(items[3])
        if items[6] == '_':
            print(line)
        parents.append(int(items[6]) - 1)
        deprels.append(items[7])
    elif len(tokens) > 0:
        sentence = " ".join(tokens)
        
        # first print the whole sentence
        print('#sentence: ' + sentence)
        c = 0        
        for i in range(len(tokens)):
            print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
            c += 1
        print()

        # find all subtrees and their respective deprels
        subtree_deprel = dict()
        for i in range(len(tokens)):
            descendants = []
            for j in range(len(tokens)):
                p = j
                while p != i and p != -1:
                    p = parents[p]
                if p == i:
                    descendants.append(j)
            subtree_deprel[" ".join(str(x) for x in descendants)] = deprels[i]

        # print all the skip-sentences
        for k in range(len(tokens)):
            for l in range(len(tokens) - k):
                if k == 0 and l == len(tokens) - 1:
                    continue
                if l > 2:
                    continue
                indices = " ".join(str(x) for x in range(k, k + l + 1))
                deprel = "<none>"
                if indices in subtree_deprel.keys():
                    deprel = subtree_deprel[indices]
                print('#skipped:\t' + indices + "\t" + " ".join(tags[x] for x in range(k, k + l + 1)) + "\t" + deprel) 
                c = 0 
                for i in range(len(tokens)):
                    if i < k or i > k + l:
                        print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
                        c += 1
                print()

            












