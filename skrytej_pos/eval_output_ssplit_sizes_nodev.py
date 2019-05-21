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


if len(sys.argv) != 9:
    print('Usage:', file=sys.stderr)
    print(sys.argv[0],
            'cs-ud-dev.forms',
            'cs-ud-dev.tags',
            'output/cs-ud-dev.tagger-embsonly-ssplit8-50.output',
            'output/cs-ud-dev.tagger-embsonly-ssplit9-50.output',
            'train/cs-ud-train.forms.ssplit8.50',
            'train/cs-ud-train.forms.ssplit9.50',
            'cs-ud-dev.invocabforms',
            'cs-ud-train.forms.495.types'
            , file=sys.stderr)
    exit()

infile, goldfile, predfile1, predfile2, trainfile1, trainfile2, testwordsfile, devwordsfile= sys.argv[1:9]


logging.info('Read in testowrds')
testwords = readtest(testwordsfile)
devwords = readtest(devwordsfile)
trainwords1 = readtrain(trainfile1)
trainwords2 = readtrain(trainfile2)
testwords1 = trainwords1.difference(trainwords2).intersection(testwords).difference(devwords)
testwords2 = trainwords2.difference(trainwords1).intersection(testwords).difference(devwords)
logging.info('Testowrds have been read in')


print(len(testwords1), len(testwords2), sep='\t')

