#!/usr/bin/env python3
#coding: utf-8

import sys
import logging

#logging.basicConfig(level=logging.DEBUG)

def readtrain(filename):
    trainwords = set()
    with open(filename) as fh:
        for line in fh:
            words = line.split()
            trainwords.update(words)
    return trainwords

def readtest(filename):
    with open(filename) as fh:
        line = fh.read()
        words = line.split()
        testwords = set(words)
    return testwords


if len(sys.argv) != 8:
    print('Usage:')
    print(sys.argv[0],
            'cs-ud-dev.forms',
            'cs-ud-dev.tags',
            'output/cs-ud-dev.tagger-embsonly-ssplit8-50.output',
            'output/cs-ud-dev.tagger-embsonly-ssplit9-50.output',
            'train/cs-ud-train.forms.ssplit8.50',
            'train/cs-ud-train.forms.ssplit9.50',
            'cs-ud-dev.invocabforms',
            )
    exit()

infile, goldfile, predfile1, predfile2, trainfile1, trainfile2, testwordsfile = sys.argv[1:8]


logging.info('Read in testowrds')
testwords = readtest(testwordsfile)
trainwords1 = readtrain(trainfile1)
trainwords2 = readtrain(trainfile2)
testwords1 = trainwords1.difference(trainwords2).intersection(testwords)
testwords2 = trainwords2.difference(trainwords1).intersection(testwords)
logging.info('Testowrds have been read in')


print(len(testwords1), len(testwords2), sep='\t')

