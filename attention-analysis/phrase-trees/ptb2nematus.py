#!/usr/bin/env python3

import re
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--input", help="PennTreebank tokenization, sentence per line")
ap.add_argument("--output", help="Output Nematus tokenization, sentence per line")
ap.add_argument("--alignment", help="Alignment file maping input tokens to output tokens")
args= ap.parse_args()

output_file = open(args.output, "w")
alignment_file = open(args.alignment, "w")

with open(args.input) as f:
    lines = f.readlines()

for line in lines:
    tokens = line.rstrip().split(" ")
    output_tokens = list()
    alignment = list()
    for i in range(len(tokens)):
        if (tokens[i] == '``' or tokens[i] == "''"):
            tokens[i] = '&quot;'
        elif (tokens[i] == '`' or tokens[i] == "'"):
            tokens[i] = '&apos;'
        elif (tokens[i] == '--'):
            tokens[i] = '-'
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
        elif (i < len(tokens) - 1 and tokens[i + 1] == "n't"):
            tokens[i] += "n"
            tokens[i + 1] = "'t"
        else:
            tokens[i] = re.sub("&", " &amp; ", tokens[i])
            tokens[i] = re.sub("'", "&apos;", tokens[i])
            tokens[i] = re.sub("-", " @-@ ", tokens[i])
            tokens[i] = re.sub("\.$", " .", tokens[i])
            tokens[i] = re.sub("\s+", " ", tokens[i])
            tokens[i] = re.sub("^\s+", "", tokens[i])
            tokens[i] = re.sub("\s+$", "", tokens[i])
        new_tokens = tokens[i].split(' ')
        output_tokens += new_tokens
        for j in range(len(new_tokens)):
            alignment.append(str(i))
    output_file.write(" ".join(output_tokens) + "\n")
    alignment_file.write(" ".join(alignment) + "\n")

            
