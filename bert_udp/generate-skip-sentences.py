#!/usr/bin/python3

import sys
import re

def generate(tokens):
    sentence = " ".join(tokens)
    print('#sentence: ' + sentence)
    
    c = 0        
    for i in range(len(tokens)):
        print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
        c += 1
    print()

    for k in range(len(tokens)):
        for l in range(len(tokens) - k):
            if k == 0 and l == len(tokens) - 1:
                continue
            print('#skipped: ' + " ".join(str(x) for x in range(k, k + l + 1))) 
            c = 0
            for i in range(len(tokens)):
                if i < k or i > k + l:
                    print(str(c) + '\t' + tokens[i] + '\t_\t_\t_\t_\t_\t_\t_\t_')
                    c += 1
            print()

tokens = list() 

for line in sys.stdin:
    line = line.rstrip('\n')
    if re.match('^#', line):
        tokens = []
    elif re.match('^[0-9]', line):
        items = line.split('\t')
        tokens.append(items[1])
    elif len(tokens) > 0:
        generate(tokens)

if len(tokens) > 0:
    generate(tokens)



