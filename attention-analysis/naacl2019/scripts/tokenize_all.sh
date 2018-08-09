# for l in cs en de es et
for l in cs en de fr fi es et
do
    tokenize.sh $l \
    < ../data/europarl/intersect.$l.out \
    > ../data/europarl_tok/intersect.$l.tok \
    &
done

