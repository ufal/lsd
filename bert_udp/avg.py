#!/usr/bin/env python3
#coding: utf-8

import sys

from collections import defaultdict

reds = defaultdict(float)
counts = defaultdict(int)

for line in sys.stdin:
    pos, red = line.split()
    reds[pos] += float(red)
    counts[pos] += 1

avgs = defaultdict(float)
for pos in reds:
    avgs[pos] = reds[pos]/counts[pos]
    print(pos, avgs[pos], sep='\t')

avg = sum(reds.values())/sum(counts.values())
print('avg', avg, sep='\t')

