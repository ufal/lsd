import numpy as np
import math
import re
import sys
from scipy.spatial import distance

e_file = np.load(sys.argv[2])
e_keys = list(e_file.keys())

w_file = open(sys.argv[1], 'r')
tokens = list()
full_sent_emb = None
s_count = 0

for line in w_file:
    line = line.rstrip('\n')
    if re.match('^#sentence: ', line):
        s_count += 1
        sys.stderr.write("Processing sentence " + str(s_count) + ".\n")
        if (s_count > 1):
            print()
        print(line)
        tokens = line.split(" ")
        tokens.pop(0)
        length = len(tokens)
        key = e_keys.pop(0)
        full_sent_emb = e_file[key]
    elif re.match('^#skipped: ', line):
        skipped = line.split(" ")
        skipped.pop(0)
        key = e_keys.pop(0)
        avg = 0
        i2 = 0
        for i in range(len(tokens)):
            if str(i) not in skipped:
                #dist = 0
                #for j in range(len(full_sent_emb[i])):
                #    dist += (e_file[key][i2][j] - full_sent_emb[i][j])**2  
                #avg += math.sqrt(dist)
                avg += distance.euclidean(e_file[key][i2], full_sent_emb[i])
                i2 += 1
        avg /= len(e_file[key])
        print(" ".join(skipped), end='\t')
        print(" ".join(map(lambda x: tokens[int(x)], skipped)), end='\t')
        print(str(avg))
print()
        

