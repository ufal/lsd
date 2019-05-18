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

def evalpreds(infile, predfile, goldfile, invtestwords, oovtestwords):
    total = 0
    correct = 0
    invtotal = 0
    invcorrect = 0
    oovtotal = 0
    oovcorrect = 0
    with open(infile) as ifh, open(predfile) as pfh, open(goldfile) as gfh:
        for words, preds, golds in zip(ifh, pfh, gfh):
            words = words.split()
            preds = preds.split()
            golds = golds.split()
            for word, pred, gold in zip(words, preds, golds):
                good = (pred == gold)
                total += 1
                if good:
                    correct += 1
                if word in invtestwords:
                    invtotal += 1
                    if good:
                        invcorrect += 1
                if word in oovtestwords:
                    oovtotal += 1
                    if good:
                        oovcorrect += 1
                logging.debug('{} {} {} {}'.format(word, pred, gold, (pred==gold)))
    return (correct/total, invcorrect/invtotal, oovcorrect/oovtotal)




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

eval_1 = evalpreds(infile, predfile1, goldfile, testwords1, testwords2)
eval_2 = evalpreds(infile, predfile2, goldfile, testwords2, testwords1)

print(*eval_1, *eval_2, sep='\t')

