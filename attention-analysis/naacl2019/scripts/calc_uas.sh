#!/usr/bin/env bash

FILES="/net/projects/LSD/naacl2019-data/experiments/ende-16h-bpe100k
"
FILE_BERT=/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA


OUTPUT_DIR=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/experiments
UAS_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/attention_uas.py
CONLLU=/net/projects/LSD/naacl2019-data/entest.conllu

source /home/limisiewicz/general/bin/activate

for f in $FILES
do
  b=$(basename $f)
  if [ ! -d  "$OUTPUT_DIR/$b/syntax" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/syntax"
  fi
  python $UAS_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -u "$OUTPUT_DIR/$b/syntax/uas" -c $CONLLU -e
done


b=$(basename $FILE_BERT)
  if [ ! -d  "$OUTPUT_DIR/$b/syntax" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/syntax"
  fi
python $UAS_SCRIPT -a "$FILE_BERT/attentions.npz" -t "$FILE_BERT/source.txt" -u "$OUTPUT_DIR/$b/syntax/uas" -c $CONLLU -e -n