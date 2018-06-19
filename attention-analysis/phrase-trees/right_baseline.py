#!/usr/bin/env python3

import sys

counter = 0
for line in sys.stdin:
    if (counter >= 10 and counter < 50):
        ending_brackets = ""
        for word in line.split():
            print ("(X " + word + " ", end="")
            ending_brackets += ")"
        print (ending_brackets)
    counter += 1    


