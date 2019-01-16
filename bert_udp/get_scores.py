import numpy as np
import math
import re

e_file = np.load('skip-sentences.npz')
e_keys  = e_file.keys()

w_file = open('skip-sentences.conllu', 'r')
tokens = list()
full_sent_emb = None

for line in w_file:
    line = line.rstrip('\n')
    if re.match('#sentence: ', line):
        print(line)
        tokens = line.split(" ")
        tokens.pop(0)
        key = e_keys.pop(0)
        full_sent_emb = e_file[key]
    elif re.match('#skipped: ', line):
        skipped = line.split(" ")
        skipped.pop(0)
        key = e_keys.pop(0)
        avg = 0
        i2 = 0
        for i in range(len(tokens)):
            if str(i) not in skipped:
                dist = 0
                for j in range(len(full_sent_emb[i])):
                    dist += (e_file[key][i2][j] - full_sent_emb[i][j])**2  
                avg += math.sqrt(dist)
                i2 += 1
        avg /= len(e_file[key])
        print(" ".join(skipped), end='\t')
        print(" ".join(map(lambda x: tokens[int(x)], skipped)), end='\t')
        print(str(avg))
