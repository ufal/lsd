#!/usr/bin/env python3
#coding: utf-8

import sys
import logging

logging.basicConfig(level=logging.INFO)

def readtest(filename):
    with open(filename) as fh:
        line = fh.read()
        words = line.split()
        testwords = set(words)
    return testwords

def evalpreds(infile, predfile, goldfile, testwords):
    total = 0
    correct = 0
    with open(infile) as ifh, open(predfile) as pfh, open(goldfile) as gfh:
        for words, preds, golds in zip(ifh, pfh, gfh):
            words = words.split()
            preds = preds.split()
            golds = golds.split()
            for word, pred, gold in zip(words, preds, golds):
                if word in testwords:
                    total += 1
                    if pred == gold:
                        correct += 1
    return total, correct




if len(sys.argv) != 8:
    print('Usage:')
    print(sys.argv[0],
            'cs-ud-dev.forms',
            'cs-ud-dev.tags',
            'output/cs-ud-dev.tagger-embsonly-ssplit',
            '-50.output',
            'train/cs-ud-train.forms.ssplit',
            '.50',
            'test/cs-ud-train.forms.ssplit',
            '.50',
            '24',
            )
    exit()

infile, goldfile, predfile_pref, predfile_suf, trainfile_pref, trainfile_suf, testfile_pref, testfile_suf, ssplits = sys.argv[1:9]


total = 0
correct = 0
for split in range(ssplits):
    testwords = readtest(testfile_pref + str(ssplit) + testfile_suf)
    t, c = evalpreds(infile, predfile_pref + str(ssplit) + predfile_suf,
            goldfile, testwords)
    total += total
    correct += correct
    logging.info(' '.join('ssplit', str(ssplit), str(c), '/', str(t), '=', (c/t) ) )
print(correct, '/', total, '=', (correct/total) )



