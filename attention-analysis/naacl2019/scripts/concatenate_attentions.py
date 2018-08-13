#!/usr/bin/env python3

import numpy as np
import argparse
import glob

ap = argparse.ArgumentParser()
ap.add_argument("--input", help="input NPZ files with attentions")
ap.add_argument("--output", help="output NPZ file containing list of attentions")
args = ap.parse_args()

attentions = list()

for filename in glob.glob(args.input):
    x = np.load(filename)
    layers = list()
    for l in range(6):
        att = x["encoder/layer_" + str(l) + "/self_attention/add:0"]
        layers.append(att)
    all_layers = np.concatenate(layers, axis=0)
    attentions.append(all_layers)
np.savez(args.output, *attentions)


