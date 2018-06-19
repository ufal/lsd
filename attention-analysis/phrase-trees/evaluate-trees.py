#!/usr/bin/env python3

from nltk.tree import Tree
import sys
import re

def get_brackets(text):
    text = re.sub("\(X", " (X ", text)
    text = re.sub("\)", " ) ", text)
    text = re.sub("[\s\r\n]+", ' ', text)
    text = re.sub("^\s+", "", text)
    text = re.sub("\s+$", "", text)
    #print(text)
    tokens = text.split(" ")
    pos = 0
    stack = list()
    brackets = list()
    for tok in tokens:
        if (tok == "(X"):
            stack.append(pos)
        elif (tok == ")"):
            if len(stack) == 0:
                print ("ERROR")
            else:
                startpos = stack.pop()
                brackets.append(str(startpos) + ' ' + str(pos - 1))
                #print(str(startpos) + ' ' + str(pos - 1))
        else:
            pos += 1
    return pos, brackets

trees1 = list()
tree = ''
for line in open(sys.argv[1], 'r'):
    if (line[0] == '('):
        if (tree != ''):
            trees1.append(tree)
            tree = ''
    tree += line
if (tree != ''):
    trees1.append(tree)

trees2 = list()
tree = ''
for line in open(sys.argv[2], 'r'):
    if (line[0] == '('):
        if (tree != ''):
            trees2.append(tree)
            tree = ''
    tree += line
if (tree != ''):
    trees2.append(tree)


trees_count = 0
if (len(trees1) != len(trees2)):
    print("ERROR: different number of sentences")
    exit(1)
else:
    trees_count = len(trees1)
    print("Number of sentences: " + str(trees_count))

total1 = 0
total2 = 0
correct = 0
for i in range(trees_count):
    wc1, br1 = get_brackets(trees1[i])
    wc2, br2 = get_brackets(trees2[i])
    if (wc1 != wc2):
        print("ERROR: diferent number of tokens in sentence " + str(i + 1))
        print(trees1[i])
        print(trees2[i])
        exit(1)
    elements = dict()
    for b in br1:
        elements[b] = 1
        total1 += 1
    for b in br2:
        if b in elements:
            correct += 1
            del elements[b]
        total2 += 1

precision = correct / total1
recall = correct / total2
f1 = 2 / (1 / precision + 1 / recall)
print("P = " + str(precision) + ", R = " + str(recall) + ", F1 = " + str(f1))

