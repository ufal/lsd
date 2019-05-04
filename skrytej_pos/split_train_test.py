#!/usr/bin/env python3
#coding: utf-8

import sys

train_file, test_file = sys.argv[1:3]

def read_sents(filename):
    result = list()
    with open(filename) as fh:
        for line in fh:
            result.append(line.split())
    return result

train_sents = read_sents(train_file)
test_sents = read_sents(test_file)

count_sents = len(train_sents)
split_position = int(count_sents / 2)
train_sents_1 = train_sents[:split_position]
train_sents_2 = train_sents[split_position:]

def sents2wordset(sentences):
    result = set()
    for s in sentences:
        result = result.union(s)
    return result


words_train_1 = sents2wordset(train_sents_1)
words_train_2 = sents2wordset(train_sents_2)
words_test = sents2wordset(test_sents)

words_test_1 = words_train_2.intersection(words_test).difference(words_train_1)
words_test_2 = words_train_1.intersection(words_test).difference(words_train_2)

print(Test1)
print(' '.join(words_test_1))

print(Test2)
print(' '.join(words_test_2))

