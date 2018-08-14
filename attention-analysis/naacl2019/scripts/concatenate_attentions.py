#!/usr/bin/env python3

import numpy as np
import sys

attentions = list()

input_files = sys.argv[1:]
output_file = input_files.pop()

for filename in input_files:
    x = np.load(filename)
    layers = list()
    for l in range(6):
        att = x["encoder/layer_" + str(l) + "/self_attention/add:0"]
        layers.append(att)
    all_layers = np.concatenate(layers, axis=0)
    attentions.append(all_layers)
np.savez(output_file, *attentions)


