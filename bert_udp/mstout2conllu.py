#!/usr/bin/env python3
#coding: utf-8

import sys
from collections import defaultdict

for line in sys.stdin:
    pcs = line.split()
    parents = defaultdict(int)
    for pc in pcs:
        p, c = pc.split('-')
        parents[int(c)] = p
    length = len(pcs) + 1  # +1 for root
    for child in range(1, length+1):  # +1 cause exclusive
        out = [child, '_', '_', '_', '_', '_', parents[child], '_', '_', '_']
        print(*out, sep='\t')
    print()





