#!/usr/bin/env python3

import re

with open(args.input) as f:
    line = f.readline()
    tokens = line.split(" ")
    oi = 0
    output_tokens = list()
    alignment = list()
    for i in range(len(tokens)):
        alignment = str(i) + '-' + str(oi) 
        if (tokens[i] == '``' or tokens[i] == "\'\'"):
            tokens[i] = '&quot;'
        elif (tokens[i] == '`' or tokens[i] == "\'"):
            tokens[i] = '&apos;'
        elif (tokens[i] == '-LRB-'):
            tokens[i] = '('
        elif (tokens[i] == '-RRB-'):
            tokens[i] = ')'
        elif (tokens[i] == '-LSB-'):
            tokens[i] = '['
        elif (tokens[i] == '-RSB-'):
            tokens[i] = ']'
        elif (tokens[i] == '-LCB-'):
            tokens[i] = '{'
        elif (tokens[i] == '-RCB-'):
            tokens[i] = '}'
        elif (i < len(tokens) - 1 and tokens[i + 1] == "n\'t"):
            tokens[i] += "n"
            tokens[i + 1] = "&apos;t"
        elif (i < len(tokens) - 1 and tokens[i + 1] == "not" \
              and (tokens[i] == "can" or tokens[i] == "Can")):
            tokens[i] += "not"
            alignment = str(i) + '-' + str(oi) + ' ' + str(i+1) + ' ' + str(oi)
        tokens[i] = re.subn("&", " &apos; ", tokens[i])
        tokens[i] = re.subn("-", " @-@ ", tokens[i])
        tokens[i] = re.subn(".$", " .", tokens[i])
        tokens[i] = re.subn("\s+", " ", tokens[i])
        tokens[i] = re.subn("^\s+", "", tokens[i])
        tokens[i] = re.subn("\s+$", "", tokens[i])
        new_tokens = tokens[i].split(' ')
        output_tokens.append(new_tokens)
        output_index += len(new_tokens)
        for j in range(len(new_tokens))
            alignment.append(i)
