#!/usr/bin/env python3
#coding: utf-8

import sys

vocab, test = sys.argv[1:3]

vocabset = set()
with open(vocab) as fh:
    for line in fh:
        vocabset.add(line.split()[0])
#print('vocab', len(vocabset))

testset = set()
with open(test) as fh:
    line = fh.read()
    testset = set(line.split())
#print('test', len(testset))

inters = testset.intersection(vocabset)
#print('intersection', len(inters))

print(' '.join(inters))


