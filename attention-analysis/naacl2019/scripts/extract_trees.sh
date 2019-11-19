#!/usr/bin/env bash

FILES="/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/BertAA-dev/
"


EXTRAXT_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/extract_trees.py
CONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-conv.conllu
CONLLUPRED=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-pred2.conllu
CONLLUGOLD=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-gold2.conllu
TRAINCONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}train-conv.conllu


source /home/limisiewicz/general/bin/activate


for f in $FILES
do

  python $EXTRAXT_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -e -c $CONLLU -o $CONLLUPRED -g $CONLLUGOLD -T $TRAINCONLLU
done

export PATH=/home/limisiewicz/udapi-python/bin:$PATH
export PYTHONPATH=/home/limisiewicz/udapi-python/:$PYTHONPATH

udapy read.Conllu files=$CONLLUGOLD zone=gold read.Conllu zone=pred files=$CONLLUPRED  eval.Conll18
