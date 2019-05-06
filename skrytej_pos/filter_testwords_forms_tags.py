#!/usr/bin/env python3
#coding: utf-8

import sys

# how to get testwords: sort words in vocabulary by frequency, take lower 90%,
# shuf, take first 1000

testwords_file, forms_file, tags_file = sys.argv[1:4]
forms_file_out = forms_file + '.filtered'
tags_file_out = tags_file + '.filtered'

# to keep sentences with test words instead of removeing them, provide an
# additional argument with any value

keep_test = False
if len(sys.argv) == 5:
    keep_test = True

testwords = set()

with open(testwords_file) as testwords_fh:
    for line in testwords_fh:
        word = line.strip()
        testwords.add(word)
        
with open(forms_file) as forms_fh, \
    open(tags_file) as tags_fh, \
    open(forms_file_out, 'w') as forms_fh_out, \
    open(tags_file_out, 'w') as tags_fh_out:
        for forms_line, tags_line in zip(forms_fh, tags_fh):
            keep_line = not keep_test
            for word in forms_line.split():
                if word in testwords:
                    keep_line = keep_test
                    break
            if keep_line:
                print(forms_line, end='', file=forms_fh_out)
                print(tags_line, end='', file=tags_fh_out)

