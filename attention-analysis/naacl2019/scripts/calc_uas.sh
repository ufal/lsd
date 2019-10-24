#!/usr/bin/env bash

#FILES="/net/projects/LSD/naacl2019-data/experiments/encs-16h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/ende-16h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/ende-1h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/ende-2h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/ende-4h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/ende-8h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/enfi-16h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/enfr-16h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/enfr-1h-bpe100k
#/net/projects/LSD/naacl2019-data/experiments/enfr-8h-bpe100k
#"
FILES="/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA
/net/projects/LSD/naacl2019-data/experiments/ende-16h-bpe100k
"

OUTPUT_DIR=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/experiments
DEPAL_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/attention_depal.py
CONLLU=/net/projects/LSD/naacl2019-data/entest.conllu

source /home/limisiewicz/general/bin/activate

for f in $FILES
do
  b=$(basename $f)
  if [ ! -d  "$OUTPUT_DIR/$b/syntax" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/syntax"
  fi
  python $DEPAL_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -d "$OUTPUT_DIR/$b/syntax/uas" -c $CONLLU -e -n -b
done

