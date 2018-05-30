#!/usr/bin/env python3

import codecs
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--txt")
ap.add_argument("--wps")
ap.add_argument("--tree")
ap.add_argument("--ali")
ap.add_argument("--out")
args = ap.parse_args()

txt_file = codecs.open(args.txt, "r", "utf-8")
wps_file = codecs.open(args.wps, "r", "utf-8")
ali_file = codecs.open(args.ali, "r", "utf-8")
tree_file = codecs.open(args.tree, "r", "utf-8")

tree = tree_file.readline()
counter = 0

for txt_line in txt_file:
    wps_line = wps_file.readline()
    ali_line = ali_file.readline()
    tree_line = tree_file.readline()
    while (tree_line and tree_line[0] != '('):
        tree = tree + tree_line
        tree_line = tree_file.readline()
    print(txt_line)
    print(tree)
    str_counter = str(counter)
    output_file = codecs.open(args.out + str_counter + '.gtree', "w", "utf-8")
    output_file.write(tree)
    output_file.close()
    #output_file = codecs.open(args.out + str_counter + '.txt', "w", "utf-8")
    #output_file.write(txt_line)
    #output_file.close()
    #output_file = codecs.open(args.out + str_counter + '.wps', "w", "utf-8")
    #output_file.write(wps_line)
    #output_file.close()
    #output_file = codecs.open(args.out + str_counter + '.ali', "w", "utf-8")
    #output_file.write(ali_line)
    #output_file.close()
    counter += 1
    tree = tree_line

        



