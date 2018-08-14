#!/usr/bin/env python3

import numpy as np
import codecs
import argparse
import sys

# load attentions from file
attentions = list()
attentions_file = np.load(sys.argv[1])
for i in range(10):
    print(attentions_file["arr_" + str(i)].shape)

