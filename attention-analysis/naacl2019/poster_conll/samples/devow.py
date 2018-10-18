#!/usr/bin/env python3
#coding: utf-8

import sys
from unidecode import unidecode

for line in sys.stdin:
    line = line.strip()
    forms = line.split(' ')
    forms_devow = list()
    for form in forms:
        form = unidecode(form)
        form = form.lower()
        form = form.replace("a", "")
        form = form.replace("e", "")
        form = form.replace("i", "")
        form = form.replace("o", "")
        form = form.replace("u", "")
        form = form.replace("y", "")
        if form == "":
            form = "_"
        forms_devow.append(form)
    print(*forms_devow, sep=' ')
    
