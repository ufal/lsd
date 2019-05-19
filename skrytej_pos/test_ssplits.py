#!/usr/bin/env python3
#coding: utf-8

import sys
import logging
from collections import Counter, defaultdict
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
            
def writetrain(filename, trainsentences, trainsentences_selected):
    with open(filename, 'w') as fh:
        for sentence_id in trainsentences_selected:
            print(trainsentences[sentence_id], end='', file=fh)
            

if len(sys.argv) != 7:
    print('Usage:')
    print(sys.argv[0],
            'cs-ud-dev.forms.1k',
            'cs-ud-train.forms.68k',
            'cs-ud-train.tags.68k',
            'train/cs-ud-train.forms.ssplit',
            'train/cs-ud-train.tags.ssplit',
            '1000',
            'test/cs-ud-train.forms.ssplit',
            )
    exit()

devfile, trainfile, trainfile_tags, sstrainfile_pref, sstrainfile_tags_pref, S, sstestfile_pref = sys.argv[1:7]

S = int(S)

def genfilename(prefix, split):
    return sstrainfile_pref + str(split) + '.' + str(S)

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
word2splits = defaultdict(list)
for split in range(10):
    logging.info('Examine ssplit ' + str(split))
    trainwords = readwords(genfilename(sstrainfile_pref, split))
    covered = uncovered.difference(trainwords)    
    for word in covered:
        word2splits[word].append(split)

# select a split for each covered test word
split2words = defaultdict(set)
for word in word2splits:
    split = random.choice(word2splits[word])
    split2words[split].add(word)

# write out the test word splits
for split in range(10):
    covered = split2words[split]
    writetest(genfilename(sstestfile_pref, split), covered)    
    uncovered.difference_update(covered)
    logging.info('Done with ssplit ' + str(split) +
            ', covered ' + str(len(covered)) + ' test words, remains ' +
            str(len(uncovered)) + ' test words')

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

logging.info('Train data have been read')

split = 10
N=len(uncovered)/2
while uncovered:
    logging.info('Construct new ssplit ' + str(split))
    
    # shuffle train
    random.shuffle(trainsentence_ids)

    # sample test words
    testwords_list = random.sample(uncovered, N)

    # take first S sentences that do not contain the test words
    while len(trainsentences_selected) != S:
        testwords = set(testwords_list[:N])
        trainsentences_selected = list()
        trainwords = set()
        for sentence_id in trainsentence_ids:
            sentwords = trainsentences_set[sentence_id]
            if not testwords.intersection(sentwords):
                trainsentences_selected.append(sentence_id)
                trainwords.update(trainsentences_set[sentence_id])
                if len(trainsentences_selected) == S:
                    break
        # satisfying split not found
        N /= 2

    # see which words we have covered, output and update
    covered = uncovered.difference(trainwords)    
    writetest(genfilename(sstrainfile_pref, split), covered)    
    writetrain(genfilename(sstestfile_pref, split), trainsentences, trainsentences_selected)    
    writetrain(genfilename(sstrainfile_tags_pref, split), trainsentences_tags, trainsentences_selected)    
    uncovered.difference_update(covered)

    logging.info('Done with ssplit ' + str(split) +
            ', covered ' + str(len(covered)) + ' test words, remains ' +
            str(len(uncovered)) + ' test words')
    
    split += 1
    N *= 2

logging.info('Done')
