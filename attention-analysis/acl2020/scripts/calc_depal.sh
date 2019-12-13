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
FILES="
"

FILE_BERT=/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/BertAA-no-softmax


OUTPUT_DIR=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/experiments
DEPAL_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/attention_depal.py
CONLLU=/net/projects/LSD/naacl2019-data/entest.conllu

source /home/limisiewicz/general/bin/activate

for f in $FILES
do
  b=$(basename $f)
  if [ ! -d  "$OUTPUT_DIR/$b/depal2" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/depal2"
  fi
  python $DEPAL_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -d "$OUTPUT_DIR/$b/depal2/depal" -c $CONLLU -e -2
done

b=$(basename $FILE_BERT)
  if [ ! -d  "$OUTPUT_DIR/$b/depal2" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/depal2"
  fi
python $DEPAL_SCRIPT -a "$FILE_BERT/attentions.npz" -t "$FILE_BERT/source.txt" -d "$OUTPUT_DIR/$b/depal2/depal" -c $CONLLU -e -2

