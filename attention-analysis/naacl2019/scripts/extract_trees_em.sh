#!/usr/bin/env bash

f=/ha/home/limisiewicz/attention_my/lsd/attention-analysis/naacl2019/BertAA/BertAA-dev/
s=$((1 + RANDOM % 10000))

EXTRAXT_SCRIPT=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/scripts/extract_trees_em.py
CONLLU=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-conv.conllu
CONLLUPRED=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-pred-${s}.conllu
CONLLUGOLD=/net/projects/LSD/attention_tomasz/lsd/attention-analysis/naacl2019/graph-extraction/${LAN}dev-gold-${s}.conllu

echo "language ${LAN}"
echo "Discarding factor ${DF}"

source /home/limisiewicz/general/bin/activate

export PATH=/home/limisiewicz/udapi-python/bin:$PATH
export PYTHONPATH=/home/limisiewicz/udapi-python/:$PYTHONPATH

python $EXTRAXT_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -e -c $CONLLU -o $CONLLUPRED -g $CONLLUGOLD -f -s $s -d ${DF}


udapy read.Conllu files=$CONLLUGOLD zone=gold read.Conllu zone=pred files=$CONLLUPRED  eval.Conll18


for i in {0..30}
do
  python $EXTRAXT_SCRIPT -a "$f/attentions.npz" -t "$f/source.txt" -e -c $CONLLU -o $CONLLUPRED -g $CONLLUGOLD -s $s
  udapy read.Conllu files=$CONLLUGOLD zone=gold read.Conllu zone=pred files=$CONLLUPRED  eval.Conll18
done