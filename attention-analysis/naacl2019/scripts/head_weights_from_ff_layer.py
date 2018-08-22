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
    hidden_kernel = x["encoder/layer_" + str(l) + "/feedforward/hidden_state/kernel:0"]
    output_kernel = x["encoder/layer_" + str(l) + "/feedforward/output/kernel:0"]
    #hidden_bias = x["encoder/layer_0/feedforward/hidden_state/bias:0"]
    #output_bias = x["encoder/layer_0/feedforward/output/bias:0"]
    #print(hidden_bias.shape)
    #print(output_bias.shape)
    print(output_kernel.shape)
    head_kernel = np.split(hidden_kernel, 16)
    for h in range(16):
        ff_matmul = np.matmul(head_kernel[h],output_kernel)
        weights[l][h] = np.max(np.matmul(head_kernel[h],output_kernel))
        w_sum += weights[l][h]
    #for h in range(16):
    #    weights[l][h] /= w_sum
print(weights)
np.savez(output_file, *weights)
