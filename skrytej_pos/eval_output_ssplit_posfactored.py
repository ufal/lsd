#!/usr/bin/env python3
#coding: utf-8

import sys
import logging

#logging.basicConfig(level=logging.DEBUG)

POS = [ 'NOUN', 'PUNCT', 'ADJ', 'VERB', 'ADP', 'PROPN', 'ADV', 'PRON', 'CONJ', 'NUM', 'DET', 'SCONJ', 'AUX', 'PART', 'SYM', 'INTJ', 'X' ]
zeros = {p: 0 for p in POS}
POS2index = {pos: index for index, pos in enumerate(POS)}

EVALS = [ 'total', 'correct', 'invtotal', 'invcorrect', 'oovtotal', 'oovcorrect' ]

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
    result = {e: zeros.copy() for e in EVALS}
    with open(infile) as ifh, open(predfile) as pfh, open(goldfile) as gfh:
        for words, preds, golds in zip(ifh, pfh, gfh):
            words = words.split()
            preds = preds.split()
            golds = golds.split()
            for word, pred, gold in zip(words, preds, golds):
                good = (pred == gold)
                result['total'][gold] += 1
                if good:
                    result['correct'][gold] += 1
                if word in invtestwords:
                    result['invtotal'][gold] += 1
                    if good:
                        result['invcorrect'][gold] += 1
                if word in oovtestwords:
                    result['oovtotal'][gold] += 1
                    if good:
                        result['oovcorrect'][gold] += 1
    return result




if len(sys.argv) != 8:
    print('Usage:')
    print(sys.argv[0],
            'cs-ud-dev.forms',
            'cs-ud-dev.tags',
            'output/cs-ud-dev.tagger-embsonly-ssplit',
            '-50.output',
            'train/cs-ud-train.forms.ssplit',
            '.50',
            'cs-ud-dev.invocabforms',
            )
    exit()

infile, goldfile, predfile_pref, predfile_suf, trainfile_pref, trainfile_suf, testwordsfile = sys.argv[1:8]

p = {
        0:1, 1:0,
        2:3, 3:2,
        4:5, 5:4,
        6:7, 7:6,
        8:9, 9:8,
    }

logging.info('Read in testowrds')
testwords = readtest(testwordsfile)
trainwords = [readtrain(trainfile_pref + str(i) + trainfile_suf) for i in range(10)]
testwords_inv = [trainwords[i].difference(trainwords[p[i]]).intersection(testwords) for i in range(10)]
testwords_oov = [testwords_inv[p[i]] for i in range(10)]
logging.info('Testowrds have been read in')

sumresult = {e: zeros.copy() for e in EVALS}

for i in range(10):
    result = evalpreds(infile, predfile_pref + str(i) + predfile_suf,
            goldfile, testwords_inv[i], testwords_oov[i])
    for e in EVALS:
        for p in POS:
            sumresult[e][p] += result[e][p]

for e in ['', 'inv', 'oov']:
    sumresult[e+'acc'] = zeros.copy()
    for p in POS:
        total = sumresult[e+'total'][p]
        if total > 0:
            sumresult[e+'acc'][p] = sumresult[e+'correct'][p] / total
        else:
            sumresult[e+'acc'][p] = -1
for e in ['', 'inv', 'oov']:
    sumresult[e+'freq'] = zeros.copy()
    total = sum(sumresult[e+'total'].values())
    for p in POS:
        sumresult[e+'freq'][p] = sumresult[e+'total'][p] / total

for e in ['acc', 'invfreq', 'invacc', 'oovfreq', 'oovacc']:
    for p in POS:
        print(sumresult[e][p], end='\t')
    print()


