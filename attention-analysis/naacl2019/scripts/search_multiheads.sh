#!/usr/bin/env bash

FILES="/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/BertAA-ml-${LAN}/
"


OUTPUT_DIR=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/experiments
UAS_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/uas_multihead.py
CONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev.conllu

source /home/limisiewicz/general/bin/activate

echo "language ${LAN}"

for f in $FILES
do
  b=$(basename $f)
  if [ ! -d  "$OUTPUT_DIR/$b/multihead-cop" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/multihead-cop"
  fi
  python $UAS_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -u "$OUTPUT_DIR/$b/multihead-cop/mhuas" -c $CONLLU -e
done
