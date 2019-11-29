#!/usr/bin/env bash

FILES="/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/BertAA-dev/
"

OUTPUT_DIR=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/experiments
UAS_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/attention_uas_multihead_max_heads.py
CONVCONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-conv4.conllu
TESTDIR=/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/
TESTCONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}test-conv4.conllu

source /home/limisiewicz/general/bin/activate

echo "language ${LAN}"
echo "number heads ${NHEADS}"
echo "number sentences ${NSENTS}"
echo "randomization"


for f in $FILES
do
  b=$(basename $f)
  if [ ! -d  "$OUTPUT_DIR/$b/multihead_h3" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/multihead_h3"
  fi
  python $UAS_SCRIPT -a "$f/attentions.npz" -ta "$TESTDIR/attentions.npz" -t "$f/source.txt"  -tt "$TESTDIR/source.txt"\
  -u "$OUTPUT_DIR/$b/multihead_h3/mhuas" -c $CONVCONLLU -tc $TESTCONLLU -e -tn --numheads $NHEADS -s $NSENTS

done
