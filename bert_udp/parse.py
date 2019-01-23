#!/usr/bin/env python3

import numpy as np
import math
import re
import sys

score = dict()
brackets = dict()
tokens = list()
tree = list()

def crossing(bracket1, bracket2):
    br1 = bracket1.split("-")
    br2 = bracket2.split("-")
    if (int(br2[0]) > int(br1[0]) and int(br2[0]) < int(br1[1]) and int(br2[1]) > int(br1[1])) or (int(br1[0]) > int(br2[0]) and int(br1[0]) < int(br2[1]) and int(br1[1]) > int(br2[1])): 
        return True
    else:
        return False

def find_roots_and_deps(bracket):
    #print("processing "+bracket)
    br = bracket.split("-")
    i = int(br[0])
    j = int(br[1])

    # for a single word, return it as a root
    if i + 1 == j:
        return i
    
    # lists of roots and sub-brackets found in the bracket
    roots = list()
    deps = list()

    # position from which longest bracket is searched for
    p = i
    # while we are not at the end of the bracket
    while (p < j):
        # the farthest possible end of the bracket
        k = j
        # we exclude the whole bracket for the search
        if (p == i):
            k -= 1
        # we search for the longest bracket from p by decreasing k
        while (k > p and not (str(p)+'-'+str(k)) in brackets):
            k -= 1
        # if no such bracket was found, add p to the set of roots, and move the pointer p
        if (k == p):
            roots.append(p)
            p += 1
        else:
            # a bracket was found, add it to the set of deps and move the poiner p 
            deps.append(str(p)+'-'+str(k))
            #print("dep: " + deps[-1])
            p = k
    if len(roots) == 0:
        #print("No root for "+bracket)
        return -1
    else:
        #print("roots: ", end='')
        #print(roots)
        for dep in deps:
            r = find_roots_and_deps(dep)
            if r == -1:
                return -1
            else:
                tree[r] = roots[0]
                #print(str(r)+'->'+str(roots[0]))
        return roots[0]

for line in sys.stdin:
    line = line.rstrip('\n')
    if re.match('^#sentence: ', line):
        print(line)
        tokens = line.split(" ")
        tokens.pop(0)
        score = {}
    elif re.match('^[0-9]', line):
        items = line.split('\t')
        skipped = items[0].split(" ")
        coef = (len(skipped) / len(tokens))**0.3
        #coef = 1
        score[skipped[0] + '-' + str(int(skipped[-1]) + 1)] = float(items[2]) / coef
        if re.match('^[\.\,\:;!\?"\-]$', items[1]):
            score[skipped[0] + '-' + str(int(skipped[-1]) + 1)] = 0
    elif line == '':
        brackets = {}
        for pair in sorted(score, key=score.__getitem__):
            cr = False
            for bracket in brackets.keys():
                if crossing(pair, bracket):
                    cr = True
                    break
            if not cr:
                #print("TRY PAIR: " + pair)
                brackets[pair] = 1
                # try to build dependency tree
                tree = [-1 for i in range(len(tokens))]
                r = find_roots_and_deps("0-"+str(len(tokens)))
                if r == -1:
                    del brackets[pair]
        tree = [-1 for i in range(len(tokens))]
        r = find_roots_and_deps("0-"+str(len(tokens)))
        for i in range(len(tokens)):
            print(str(i + 1) + '\t' + tokens[i] + '\t_\t_\t_\t_\t' + str(tree[i] + 1))
        print()
