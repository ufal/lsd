#!/usr/bin/env python3

import numpy as np

attentions = list()

for i in range(100):
    filename = "sent-per-file-out/s" + str(i) + ".att.npz"
    x = np.load(filename)
    layers = list()
    for l in range(6):
        att = x["encoder/layer_" + str(l) + "/self_attention/add:0"]
        layers.append(att)
    all_layers = np.concatenate(layers, axis=0)
    #print(all_layers)
    attentions.append(all_layers)
    #print("File " + filename + " has been read.")
np.savez("attentions", *attentions)


