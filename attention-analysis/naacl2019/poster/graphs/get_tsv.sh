cd tsv_origs/
for f in *tsv
do
    cat $f ../blank.txt | \
        sed -e 's/ *//' -e 's/\. /\t/' \
        -e 's/[[:space:]]*software[[:graph:]]*[[:space:]]*/\t/' \
        -e 's/CUNI x-ling (Praha)/2/' -e 's/[A-Z].*)/1/' \
        -e 's/\t1\t.*/&\t/' -e 's/\t2\t\(.*\)/&\t\1/' \
        > tmp
    head -n 3 tmp > ../$f
    tail -n 1 tmp >> ../$f
    rm tmp
done

