
# 1st arg = number of sentences
if [ -z $1 ]
then
    S=10
else
    S=$1
fi

SR=/net/projects/LSD/attention-analysis/naacl2019/
R=$(pwd)

mkdir -p matrices
cd matrices

SENTENCES=$(seq 0 $S)

for s in $SENTENCES
do
    mkdir -p s$s
    $SR/scripts/generate_html.sh $s 15
done

$SR/scripts/attentions2tree.py -a $R/attentions.npz -t $R/source.txt -s $SENTENCES -D -v '' -e

