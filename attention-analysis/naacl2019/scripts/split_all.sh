# in WMT15 there are: cs en de fr fi
# (and we are also doing es et just in case)

D=/net/projects/LSD/naacl2019-data/

for l in cs en de fr fi es et
do
    ./split.sh $D/europarl/intersect.$l.tok &
done

