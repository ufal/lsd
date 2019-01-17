#!/usr/bin/python3

import sys
import re

gp = list()
gold = open(sys.argv[1], 'r')
for line in gold:
    line = line.rstrip('\n')
    if re.match('^[0-9]', line):
        items = line.split('\t')
        gp.append(items[6])
        #print(items[0])

pp = list()
parsed = open(sys.argv[2], 'r')
for line in parsed:
    line = line.rstrip('\n')
    if re.match('^[0-9]', line):
        items = line.split('\t')
        pp.append(items[6])
        #print(items[0])

if (len(pp) != len(gp)):
    print("Different number of tokens: " + str(len(pp)) + " != " + str(len(gp)))
    exit()

correct = 0
for i in range(len(gp)):
    if gp[i] == pp[i]:
        correct += 1
print(str(correct/len(pp)))
