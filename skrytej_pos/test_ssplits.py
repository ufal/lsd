#!/usr/bin/env python3
#coding: utf-8

import sys
import logging
from collections import Counter
import random

logging.basicConfig(level=logging.INFO)

# set
def readwords(filename):
    result = set()
    with open(filename) as fh:
        for line in fh:
            words = line.split()
            result.update(words)
    return result

# Counter
def readtest(filename):
    result = Counter()
    with open(filename) as fh:
        for line in fh:
            words = line.split()
            result.update(words)
    return result

def readsentences(filename):
    sentences = list()
    sentences_set = list()
    with open(filename) as fh:
        for line in fh:
            sentences.append(line)
            words = line.split()
            sentences_set.append(set(words))
    return sentences, sentences_set

def readtags(filename):
    with open(filename) as fh:
        return fh.readlines()

# write a set of testwords to a file
def writetest(filename, testwords):
    with open(filename, 'w') as fh:
        print(' '.join(testwords), file=fh)
            

if len(sys.argv) != 8:
    print('Usage:')
    print(sys.argv[0],
            'cs-ud-dev.forms.1k',
            'cs-ud-train.forms.68k',
            'cs-ud-train.tags.68k',
            'train/cs-ud-train.forms.ssplit',
            '1000',
            'test/cs-ud-train.forms.ssplit',
            )
    exit()

devfile, trainfile, trainfile_tags, sstrainfile_pref, S, sstestfile_pref = sys.argv[1:8]


logging.info('Read in test words')

# Counter of test words
testwords = readtest(devfile)

# test words not yet covered by a train set
uncovered = set(testwords.keys())

# cannot cover this
del testwords['.']
uncovered.discard('.')

logging.info('Test words have been read in, total test words: ' + str(len(uncovered)))

# first search through existing train splits
split = 0
while split < 10:
    logging.info('Examine ssplit ' + str(split))
    sstrainfile = sstrainfile_pref + split + '.' + S
    trainwords = readwords(sstrainfile)
    covered = uncovered.difference(trainwords)    
    sstestfile = sstestfile_pref + split + '.' + S
    writetest(sstestfile, covered)    
    uncovered.difference_update(covered)
    logging.info('Done with ssplit ' + str(split) +
            ', covered ' + str(len(covered)) + ' test words, remains ' +
            str(len(uncovered)) + ' test words')
    split += 1


# then generate new train splits covering missing words
logging.info('Move on to generating new train splits to cover the rest')
logging.info('Read in train data')

# sentence id -> string of words (with endlines)
# sentence id -> set of words
trainsentences, trainsentences_set = readsentences(trainfile)

# sentence id -> string of tags (with endlines)
trainsentences_tags = readtags(trainfile_tags)

# for shuffling
trainsentence_ids = list(range(len(trainsentences)))

# for iterating
testwords_ordered = [word for (word, count) in testwords.most_common()]
testword_id = 0

s = int(S)

logging.info('Train data have been read')

while uncovered:
    logging.info('Construct new ssplit ' + str(split))
    
    # select word to cover
    while testwords_ordered[testword_id] not in uncovered:
        testword_id += 1
    testword = testwords_ordered[testword_id]

    # shuffle train
    random.shuffle(trainsentence_ids)

    # take first N sentences that do not contain the word
    trainsentences_selected = list()
    for sentence_id in trainsentence_ids:
        if testword not in trainsentences_set[sentence_id]:
            trainsentences_selected.append(sentence_id)
        if len(trainsentences_selected) == s:
            break
        

    # see which words we have covered

    # output, update

    logging.info('Done with ssplit ' + str(split) +
            ', covered ' + str(len(covered)) + ' test words, remains ' +
            str(len(uncovered)) + ' test words')
    split += 1


logging.info('Done')
