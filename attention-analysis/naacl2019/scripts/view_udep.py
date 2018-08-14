#!/usr/bin/env python3
#coding: utf-8

import sys

COMPACT = 28

# at start or end of line, symbol is / or \ and also the --- is drawn
# in the middle, symbol is |
def draw_line(line_list, layer, symbol='|'):
    # make sure there is space
    if len(line_list) <= layer:
        spaces = [' '] * (layer - len(line_list) + 1)
        line_list.extend(spaces)
    # put symbol
    line_list[layer] = symbol
    # add ---
    if symbol != '|':
        for l in range(layer):
            if line_list[l] == ' ':
                line_list[l] = '-'

def print_sentence(words, links):
    assert len(words) == len(links)
    length = len(words)

    # construct graph
    token_lines = [ [' '] for i in range(length)  ]
    intra_lines = [ [' '] for i in range(length)  ]
    # lists of links of given legth
    longer_links = [ [] for i in range(length) ]
    for i in range(length):
        for l in links[i]:
            link_length = l-i
            assert link_length > 0, "Links must only go left to right"

            if link_length == 1:
                # neighbours are special
                if token_lines[i][0] == '/':
                    token_lines[i][0] = 'X'
                    intra_lines[i][0] = '|'
                    token_lines[l][0] = '/'
                else:
                    token_lines[i][0] = '\\'
                    intra_lines[i][0] = '|'
                    token_lines[l][0] = '/'
            else:
                # put off for now
                longer_links[link_length].append( (i, l) )

    # now go over the longer links from shortest to longest
    for link_length in range(length):
        for i, l in longer_links[link_length]:
            # find a free layer to put the link into
            layer = 0
            ok = False
            while not ok:
                layer += 3
                ok = True
                # check intra lines
                for m in range(i, l):
                    if len(intra_lines[m]) > layer:
                        if intra_lines[m][layer] == '|':
                            ok = False
                # check token lines
                for m in range(i, l+1):
                    if len(token_lines[m]) > layer:
                        if token_lines[m][layer] == '\\':
                            ok = False
                        if token_lines[m][layer] == '|':
                            ok = False
                        if token_lines[m][layer] == '/':
                            ok = False
            # draw the link
            assert ok
            draw_line(token_lines[i], layer, '\\')
            draw_line(intra_lines[i], layer, '|')
            for m in range(i+1, l):
                draw_line(token_lines[m], layer, '|')
                draw_line(intra_lines[m], layer, '|')
            draw_line(token_lines[l], layer, '/')

    # print graph
    max_word_length = max([len(w) for w in words])
    for i in range(length):
        # word line
        word = words[i]
        intro = ' ' if i < 10 else ''
        spaces = ' ' * (max_word_length - len(word) + 1)
        print(intro, str(i), spaces, word, '-', *token_lines[i], sep='')
        
        # intra line
        if length < COMPACT:
            spaces = ' ' * (max_word_length + 4)
            print(spaces, *intra_lines[i], sep='')

sentid = 0
words = []
links = []
for filename in sys.argv[1:]:
    with open(filename) as fh:
        for line in fh:
            if line != '\n':
                if line.startswith('#'):
                    continue
                fields = line.strip('\n').split('\t')
                assert len(fields) == 3
                assert int(fields[0]) == len(words)
                words.append(fields[1])
                if fields[2] != '':
                    links.append([int(l) for l in fields[2].split(',')])
                else:
                    links.append([])
            else:
                print()
                print("=====", "SENTENCE", sentid, "FILE", filename, "=====")
                print()
                print_sentence(words, links)
                sentid += 1
                words = []
                links = []


