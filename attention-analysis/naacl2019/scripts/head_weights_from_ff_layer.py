#!/usr/bin/env python3

import numpy as np
import sys

weights = np.zeros((6,16))

input_file = sys.argv[1]
output_file = sys.argv[2]

x = np.load(input_file)
for l in range(6):
    head_weights = list()
    w_sum = 0
    head = np.split(x["encoder/layer_" + str(l) + "/self_attention/output_proj/kernel:0"], 16)
    for h in range(16):
        weights[l][h] = np.mean(np.absolute(head[h]))
        w_sum += weights[l][h]
    for h in range(16):
        weights[l][h] /= w_sum
print(weights)
np.savez(output_file, *weights)
