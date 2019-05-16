#!/usr/bin/env python3
#coding: utf-8

import sys
import logging

#logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) != 7:
    print('Usage:')
    print(sys.argv[0], 'cs-ud-dev.forms',
            'cs-ud-dev.tagger-embs-only-train1.output',
            'cs-ud-dev.tagger-embs-only-train2.output',
            'cs-ud-dev.tags',
            'testwords_lc_A',
            'testwords_lc_B',
            )
    exit()

infile, predfile1, predfile2, goldfile, testwordsfileA, testwordsfileB = sys.argv[1:7]

def readtest(filename):
    testwords = set()
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
                if word.lower() in testwords:
                    total += 1
                    if pred == gold:
                        correct += 1
                    logging.debug('{} {} {} {}'.format(word, pred, gold, (pred==gold)))
    return correct/total


logging.info('Read in testowrds')
testwordsA = readtest(testwordsfileA)
testwordsB = readtest(testwordsfileB)
logging.info('Testowrds have been read in')

e_1A = evalpreds(infile, predfile1, goldfile, testwordsA)
e_1B = evalpreds(infile, predfile1, goldfile, testwordsB)
e_2A = evalpreds(infile, predfile2, goldfile, testwordsA)
e_2B = evalpreds(infile, predfile2, goldfile, testwordsB)

print(e_1A, e_1B, e_2B, e_2A, sep='\t',  )

