#!/usr/bin/env python3
#coding: utf-8

import sys

commons_file = sys.argv[1]

commons_set = set()
with open(commons_file) as commons:
    for line in commons:
        commons_set.add(line.strip())

for line in sys.stdin:
    ok = True
    line = line.strip()
    src, tgt = line.split('\t')
    for token in src.split():
        if token not in commons_set:
            ok = False
    for token in tgt.split():
        if token not in commons_set:
            ok = False
    if ok:
        print(line)

