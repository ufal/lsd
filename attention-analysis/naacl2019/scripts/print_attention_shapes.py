#!/usr/bin/env python3

import numpy as np
import codecs
import argparse
import sys

# load attentions from file
attentions = list()
attentions_file = np.load(sys.argv[1])

print(attentions_file)

fns=attentions_file.files
#print('\n'.join(fns))
#print(len(fns))

#for i in range(10):
for i in range(111):
    # pass
    print(attentions_file["arr_" + str(i)].shape)

