#!/usr/bin/env bash

FILES="/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/BertAA-dev/
"


OUTPUT_DIR=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/experiments
UAS_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/attention_uas.py
CONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev.conllu

source /home/limisiewicz/general/bin/activate

for f in $FILES
do
  b=$(basename $f)
  if [ ! -d  "$OUTPUT_DIR/$b/syntax+pos+hard" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/syntax+pos+hard"
  fi
  python $UAS_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -u "$OUTPUT_DIR/$b/syntax+pos+hard/uas" -c $CONLLU -e
done