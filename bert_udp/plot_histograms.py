#!/usr/bin/env python3

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from collections import defaultdict

avg = defaultdict(float)
total = defaultdict(int)
ind_value = list()
ind_is_leaf = list()

for line in sys.stdin:
    line = line.rstrip('\n')
    items = line.split("\t")
    if len(items) > 5 and int(items[4]) == 1: # and items[2] == 'AUX':
        b = 'F'
        if items[3] == '<none>':
            b = 'T'
        key = items[2] + " " + b
        ind_value.append(float(items[5]))
        if items[3] == '<none>':
            ind_is_leaf.append('b')
        else:
            ind_is_leaf.append('y')
        avg[key] += float(items[5])
        total[key] += 1

newavg = dict()

for key in avg.keys():
    if total[key] >= 20:
        newavg[key] = avg[key] / total[key]

    print(newavg)

plt.figure(1)
x = np.arange(len(newavg))
sorted_keys = sorted(newavg, key=newavg.get)
plt.bar(x, height=[newavg[k] for k in sorted_keys]) #, width=[total[k] / 150 for k in sorted_keys])
plt.xticks(x, labels=sorted_keys, rotation='vertical')
#plt.show()
plt.savefig('pos.pdf')

plt.figure(2)
s = np.argsort(ind_value)
x = np.arange(len(s))
plt.bar(x, height=[ind_value[k] for k in s], color=[ind_is_leaf[k] for k in s])
#plt.show()
plt.savefig('inst.pdf')

