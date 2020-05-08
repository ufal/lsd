#!/usr/bin/env bash

export PATH=/home/limisiewicz/udapi-python/bin:$PATH
export PYTHONPATH=/home/limisiewicz/udapi-python/:$PYTHONPATH

source /home/limisiewicz/general/bin/activate



array=()
while IFS=  read -r -d $'\0'; do
    array+=("$REPLY")
done < <(find ../graph-extraction \( -name "*dev.conllu" -o -name "*train.conllu" \) -print0)

for f in "${array[@]}"
do
  udapy read.Conllu files=$f attention.AttentionConvert  write.Conllu > "${f%.*}"-conv.conllu
done

