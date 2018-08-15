#!/usr/bin/env python3

import gzip
import random

base = "data/europarl/europarl-v7.cs-en.en.gz"

dykt = {"cs": {}, "de": {}, "es": {}, "et": {}, "fi": {}, "fr":            {}}

with gzip.open("data/europarl/europarl-v7.cs-en.en.gz") as fen, gzip.open("data/europarl/europarl-v7.cs-en.cs.gz") as fcs:
    for line1, line2 in zip(fen, fcs):
        ln_en = line1.decode("utf-8").rstrip("\n")
        ln_cs = line2.decode("utf-8").rstrip("\n")

        if ln_en == "":
            continue

        while ln_en in dykt["cs"]:
            ln_en += "#"

        if ln_cs != "":
            dykt["cs"][ln_en] = ln_cs

print("len of dyk cs: {}".format(len(dykt["cs"])))

for lang in ["de", "es", "et", "fi", "fr"]:
    with gzip.open("data/europarl/europarl-v7.{}-en.en.gz".format(lang)) as fen, gzip.open("data/europarl/europarl-v7.{}-en.{}.gz".format(lang, lang)) as ftgt:
        for line1, line2 in zip(fen, ftgt):
            ln_en = line1.decode("utf-8").rstrip("\n")
            ln_tgt = line2.decode("utf-8").rstrip("\n")

            if ln_en not in dykt["cs"]:
                # print("Not in en-cs: {} {} {}".format(lang, ln_en, len(dykt[lang])))
                continue

            while ln_en in dykt[lang]:
                ln_en += "#"

            if ln_tgt != "":
                dykt[lang][ln_en] = ln_tgt

prefix = "data/europarl/intersect."

with open(prefix + "cs.out", "w") as fcs, open(prefix + "en.out", "w") as fen, open(prefix + "de.out", "w") as fde, open(prefix + "es.out", "w") as fes, open(prefix + "et.out", "w") as fet, open(prefix + "fi.out", "w") as ffi, open(prefix + "fr.out", "w") as ffr:

    ens = list(dykt["cs"].keys())
    random.shuffle(ens)

    for en in ens:
        if all(en in dykt[l] for l in ["de","es","et","fi","fr"]):

            
            print(dykt["cs"][en], file=fcs)
            print(dykt["de"][en], file=fde)
            print(dykt["es"][en], file=fes)
            print(dykt["et"][en], file=fet)
            print(dykt["fi"][en], file=ffi)
            print(dykt["fr"][en], file=ffr)

            en_oklestena = en.rstrip("#")

            print(en_oklestena, file=fen)
