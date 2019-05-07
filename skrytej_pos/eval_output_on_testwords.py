#!/usr/bin/env python3
#coding: utf-8

import sys
import logging


if len(sys.argv) != 5:
    print('Usage:')
    print(sys.argv[0], 'cs-ud-dev.forms',
            'cs-ud-dev.tagger-embs-only-train1.output',
            'cs-ud-dev.tags',
            'testwords_lc_1')
    exit()

infile, predfile, goldfile, testwordsfile = sys.argv[1:5]



logging.info('Read in testowrds')
testwords = set()
with open(testwordsfile) as fh:
    line = fh.read()
    words = line.split()
    testwords = set(words)
logging.info('Testowrds have been read in')

total = 0
correct = 0

with open(infile) as ifh, open(predfile) as pfh, open(goldfile) as gfh:
    for words, preds, golds in zip(ifh, pfh, gfh):
        words = words.split()
        preds = preds.split()
        golds = golds.split()
        for word, pred, gold in zip(words, preds, golds):
            if word.lower() in testwords:
                total += 1
                if pred == gold:
                    correct += 1

print(correct, '/', total, '=', (correct/total))


