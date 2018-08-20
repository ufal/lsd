
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
    $SR/scripts/generate_html.sh $s
done

# all heads, aggreg and not-aggreg
$SR/scripts/attentions2tree.py -a $R/attentions.npz -t $R/source.txt -s $SENTENCES -D -v kall   -e
$SR/scripts/attentions2tree.py -a $R/attentions.npz -t $R/source.txt -s $SENTENCES -D -v n-kall -e -n

# for each layer
for l in $(seq 0 5)
do
    # for each head
    for k in $(seq 0 15)
    do
        # aggreg and not-aggreg
        $SR/scripts/attentions2tree.py -a $R/attentions.npz -t $R/source.txt -s $SENTENCES -D -v k$k   -k $k -l $l -e
        $SR/scripts/attentions2tree.py -a $R/attentions.npz -t $R/source.txt -s $SENTENCES -D -v n-k$k -k $k -l $l -e -n
    done
done

