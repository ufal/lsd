#!/usr/bin/env python3

import sys
import re

ID = 0
PARENT = 6

def readfile(filename):
    result = list()
    cur_sent = dict()
    with open(filename, 'r') as infile:
        for line in infile:
            items = line.split()
            if items[ID].isdigit():
                cur_sent[items[ID]] = items[PARENT]

gp = readfile(sys.argv[1])
pp = readfile(sys.argv[2])


if (len(pp) != len(gp)):
    print("Different number of tokens: " + str(len(pp)) + " != " + str(len(gp)))
    exit()

correct = 0
for i in range(len(gp)):
    if gp[i] == pp[i]:
        correct += 1
print(str(correct/len(pp)))
