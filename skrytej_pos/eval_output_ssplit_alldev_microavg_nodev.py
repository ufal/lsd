#!/usr/bin/env python3
#coding: utf-8

import sys
import logging

#logging.basicConfig(level=logging.INFO)

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

def evalpreds(infile, predfile, goldfile, testwords):
    total = 0
    correct = 0
    with open(infile) as ifh, open(predfile) as pfh, open(goldfile) as gfh:
        for words, preds, golds in zip(ifh, pfh, gfh):
            words = words.split()
            preds = preds.split()
            golds = golds.split()
            for word, pred, gold in zip(words, preds, golds):
                #if gold != 'PUNCT':
                    if word in testwords:
                        total += 1
                        if pred == gold:
                            correct += 1
    return total, correct




if len(sys.argv) != 9:
    print('Usage:')
    print(sys.argv[0],
            'cs-ud-dev.forms',
            'cs-ud-dev.tags',
            'output/cs-ud-dev.tagger-hidden-new-ssplit',
            '-30000.output',
            'train/cs-ud-train.forms.ssplit',
            '.30000',
            'cs-ud-dev.invocabforms',
            'cs-ud-train.forms.495.types'
            )
    exit()

infile, goldfile, predfile_pref, predfile_suf, trainfile_pref, trainfile_suf, testwordsfile, devwordsfile = sys.argv[1:9]

testwords = readtest(testwordsfile)
devwords = readtest(devwordsfile)

total_seen = 0
correct_seen = 0
total_unseen = 0
correct_unseen = 0

avgs_seen = list()
avgs_unseen = list()

for ssplit1 in range(0, 10, 2):

    ssplit2 = ssplit1 + 1

    trainwords1 = readtrain(trainfile_pref + str(ssplit1) + trainfile_suf)
    trainwords2 = readtrain(trainfile_pref + str(ssplit2) + trainfile_suf)
    
    testwordsA = trainwords1.difference(trainwords2).intersection(testwords).difference(devwords)
    testwordsB = trainwords2.difference(trainwords1).intersection(testwords).difference(devwords)
    
    predfile1 = predfile_pref + str(ssplit1) + predfile_suf
    predfile2 = predfile_pref + str(ssplit2) + predfile_suf
    
    t1_seen, c1_seen = evalpreds(infile, predfile1, goldfile, testwordsA)
    t2_seen, c2_seen = evalpreds(infile, predfile2, goldfile, testwordsB)

    t1_unseen, c1_unseen = evalpreds(infile, predfile1, goldfile, testwordsB)
    t2_unseen, c2_unseen = evalpreds(infile, predfile2, goldfile, testwordsA)

    avg1_seen = c1_seen/t1_seen
    avg1_unseen = c1_unseen/t1_unseen
    avg2_seen = c2_seen/t2_seen
    avg2_unseen = c2_unseen/t2_unseen

    total_seen += t1_seen + t2_seen
    correct_seen += c1_seen + c2_seen
    total_unseen += t1_unseen + t2_unseen
    correct_unseen += c1_unseen + c2_unseen
    avgs_seen.append(avg1_seen)
    avgs_seen.append(avg2_seen)
    avgs_unseen.append(avg1_unseen)
    avgs_unseen.append(avg2_unseen)

    logging.info('ssplit {}, seen {}/{} = {}'.format(ssplit1, c1_seen, t1_seen, avg1_seen))
    logging.info('ssplit {}, unsn {}/{} = {}'.format(ssplit1, c1_unseen, t1_unseen, (c1_unseen/t1_unseen)))
    logging.info('ssplit {}, seen {}/{} = {}'.format(ssplit2, c2_seen, t2_seen, (c2_seen/t2_seen)))
    logging.info('ssplit {}, unsn {}/{} = {}'.format(ssplit2, c2_unseen, t2_unseen, (c2_unseen/t2_unseen)))


acc_s = correct_seen/total_seen
acc_n = correct_unseen/total_unseen

import statistics 
std_s = statistics.stdev(avgs_seen)
std_n = statistics.stdev(avgs_unseen)

logging.info('SEEN {}/{} = {}'.format(correct_seen, total_seen, acc_s))
logging.info('UNSN {}/{} = {}'.format(correct_unseen, total_unseen, acc_n))

print(acc_s, acc_n, (acc_s - acc_n), std_s, std_n, sep="\t")

