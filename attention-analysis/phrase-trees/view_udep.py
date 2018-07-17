#!/usr/bin/env python3
#coding: utf-8

import sys

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
    for i in range(length):
        for l in links[i]:
            assert i < l, "Links must only go further in the file"

            if l == i+1:
                # neighbours are special
                token_lines[i][0] = '+'
                intra_lines[i][0] = '|'
                token_lines[l][0] = '+'
            else:
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
        spaces = ' ' * (max_word_length + 4)
        print(spaces, *intra_lines[i], sep='')


words = []
links = []
for line in sys.stdin:
    fields = line.strip('\n').split('\t')
    if len(fields) == 0:
        print_sentence(words, links)
        words = []
        links = []
    else:
        assert len(fields) == 3
        assert int(fields[0]) == len(words)
        words.append(fields[1])
        if fields[2] != '':
            links.append([int(l) for l in fields[2].split(',')])
        else:
            links.append([])
if len(words) > 0:
    print_sentence(words, links)

