#!/usr/bin/env bash

FILES="/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/BertAA-dev/
"

OUTPUT_DIR=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/experiments
UAS_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/attention_uas_multihead.py
CONVCONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-conv.conllu
CONVTRAINCONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}train-conv.conllu
#CONVCONLLU=/tmp/conv.conllu
#CONVTRAINCONLLU=/tmp/train-conv.conllu

#export PATH=/home/limisiewicz/udapi-python/bin:$PATH
#export PYTHONPATH=/home/limisiewicz/udapi-python/:$PYTHONPATH
#
source /home/limisiewicz/general/bin/activate
#
#udapy read.Conllu files=$CONLLU attention.AttentionConvert  write.Conllu > $CONVCONLLU
#udapy read.Conllu files=$TRAINCONLLU attention.AttentionConvert  write.Conllu > $CONVTRAINCONLLU
echo "language ${LAN}"

for f in $FILES
do
  b=$(basename $f)
  if [ ! -d  "$OUTPUT_DIR/$b/multihead_all_hard" ]
  then
    mkdir -p "$OUTPUT_DIR/$b/multihead_all_hard"
  fi
  python $UAS_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -u "$OUTPUT_DIR/$b/multihead_all/mhuas_hard" -c $CONVCONLLU -e -T $CONVTRAINCONLLU
done
