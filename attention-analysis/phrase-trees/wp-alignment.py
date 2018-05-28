#!/usr/bin/env python3

import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--wordpieces", help="Wordpieces")
ap.add_argument("--alignment", help="Input alignment file")

args= ap.parse_args()

wps_file = open(args.wordpieces, "r")
ali_file = open(args.alignment, "r")

for line in wps_file:
    tokens = line.rstrip().split(" ")
    alignment = ali_file.readline()
    input_ali = alignment.rstrip().split(" ")
    output_ali = list()
    ali_index = 0
    for tok in tokens:
        output_ali.append(str(input_ali[ali_index]))
        if (tok[-1] == '_'):
            ali_index += 1
    print(" ".join(output_ali))




    




