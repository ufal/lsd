#!/usr/bin/env python3
#coding: utf-8

import sys

# cs-ud-dev.invocabforms cs-ud-train.forms.split2.5000 > cs-ud-train.forms.B.5000 

test, train = sys.argv[1:3]

trainset = set()
with open(train) as fh:
    for line in fh:
        words = line.split()
        for word in words:
            trainset.add(word)
#print('test', len(testset))

testset = set()
with open(test) as fh:
    line = fh.read()
    testset = set(line.split())
#print('test', len(testset))

inters = trainset.intersection(testset)
#print('intersection', len(inters))

print(' '.join(inters))


