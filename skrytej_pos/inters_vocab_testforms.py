#!/usr/bin/env python3
#coding: utf-8

import sys

# inters_vocab_testforms.py cs_vocab_25k.tsv cs-ud-dev.forms cs-ud-dev.forms > cs-ud-dev.invocabforms

vocab, test = sys.argv[1:3]

vocabset = set()
with open(vocab) as fh:
    for line in fh:
        vocabset.add(line.split()[0])
#print('vocab', len(vocabset))

testset = set()
with open(test) as fh:
    for line in fh:
        words = line.split()
        for word in words:
            testset.add(word)
#print('test', len(testset))

inters = testset.intersection(vocabset)
#print('intersection', len(inters))

print(' '.join(inters))


