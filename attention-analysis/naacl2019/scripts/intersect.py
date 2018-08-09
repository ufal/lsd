#!/usr/bin/env python3

import gzip

base = "data/europarl/europarl-v7.cs-en.en.gz"

dykt = {"cs": {}, "de": {}, "es": {}, "et": {}}

with gzip.open("data/europarl/europarl-v7.cs-en.en.gz") as fen, gzip.open("data/europarl/europarl-v7.cs-en.cs.gz") as fcs:
    for line1, line2 in zip(fen, fcs):
        ln_en = line1.decode("utf-8").rstrip("\n")
        ln_cs = line2.decode("utf-8").rstrip("\n")

        while ln_en in dykt["cs"]:
            ln_en += "#"

        dykt["cs"][ln_en] = ln_cs

print("len of dyk cs: {}".format(len(dykt["cs"])))

for lang in ["de", "es", "et"]:
    with gzip.open("data/europarl/europarl-v7.{}-en.en.gz".format(lang)) as fen, gzip.open("data/europarl/europarl-v7.{}-en.{}.gz".format(lang, lang)) as ftgt:
        for line1, line2 in zip(fen, ftgt):
            ln_en = line1.decode("utf-8").rstrip("\n")
            ln_tgt = line2.decode("utf-8").rstrip("\n")

            if ln_en not in dykt["cs"]:
                # print("Not in en-cs: {} {} {}".format(lang, ln_en, len(dykt[lang])))
                continue

            while ln_en in dykt[lang]:
                ln_en += "#"

            dykt[lang][ln_en] = ln_tgt

prefix = "data/europarl/intersect."

with open(prefix + "cs.out", "w") as fcs, open(prefix + "en.out", "w") as fen, open(prefix + "de.out", "w") as ffr, open(prefix + "es.out", "w") as fes, open(prefix + "et.out", "w") as fde:

    for en, cs in dykt["cs"].items():
        if all(en in dykt[l] for l in ["de","es","et"]):

            print(dykt["cs"][en], file=fcs)
            print(dykt["de"][en], file=ffr)
            print(dykt["es"][en], file=fes)
            print(dykt["et"][en], file=fde)

            en_oklestena = en.rstrip("#")

            print(en_oklestena, file=fen)
