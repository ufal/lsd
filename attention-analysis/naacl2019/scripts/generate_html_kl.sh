H=$1
L=5
S=100

function IMG () {
    I=$1
    echo '<a href="'$I'"><img src="'$I'"></a>'
}

for k in $(seq 0 $H)
do
for l in $(seq 0 $L)
do

    F=k$k-l$l.html

    echo '<a href="'$F'">'Layer $l, head $k'</a><br>'

    echo '<!DOCTYPE html>' > $F
    echo '<html><head><title>'Layer $l, head $k'</title><style>' >> $F
    echo 'img {float: left; height: 400px; width: 400px; }' >> $F
    echo '</style></head><body>' >> $F
    echo '<h1>'Layer $l, head $k'</h1>' >> $F

    for s in $(seq 0 $S)
    do
        IMG "s$s/k$k-l$l.png" >> $F
    done

    echo '</body></html>' >> $F

done
done

