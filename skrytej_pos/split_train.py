#!/usr/bin/env python3
#coding: utf-8

import sys

train_file = sys.argv[1]

def read_sents(filename):
    result = list()
    with open(filename) as fh:
        for line in fh:
            result.append(line.split())
    return result

train_sents = read_sents(train_file)

count_sents = len(train_sents)
split_position = int(count_sents / 2)
train_sents_1 = train_sents[:split_position]
train_sents_2 = train_sents[split_position:]

with open(train_file + '.split1', 'w') as outfile:
    for sent in train_sents_1:
        print(' '.join(sent), file=outfile)
with open(train_file + '.split2', 'w') as outfile:
    for sent in train_sents_2:
        print(' '.join(sent), file=outfile)


