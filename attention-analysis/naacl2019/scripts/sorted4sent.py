#!/usr/bin/env python3
#coding: utf-8

import sys

print('''
<!DOCTYPE html>
<html><head><title>4sent sorted podle plutkovitosti</title><style>
h3 {float: left;  }
img {float: left; height: 200px; width: 200px; }
hr {clear: both; margin-top: 1px; margin-bottom: 1px }
</style></head><body>
<h1>4sent sorted podle plutkovitosti (sents 0-4, not aggreg)</h1>
''')

for line in sys.stdin:
    fields = line.split()
    layer = fields[3]
    head = fields[5]
    balustradeness = fields[7]
    bal_s = balustradeness[:4]

    print('<h3>Layer', layer, '<br>head', head, '<br>bal.', bal_s, '</h3>')
    for s in range(5):
        url = 's{}/n-k{}-l{}.png'.format(s, head, layer)
        print('<a href="'+url+'"><img src="'+url+'"></a>')
    print('<hr>')

print('</body></html>')
