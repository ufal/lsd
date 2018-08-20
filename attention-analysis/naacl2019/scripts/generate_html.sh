
# 1st arg = number of sentence
S=$1

# 2nd arg = index of last head
H=$2

F=s$S.html

echo '<!DOCTYPE html>' > $F
echo '<html><head><title>'Sentence $S'</title><style>' >> $F
echo 'img {float: left; height: 200px; width: 200px; }' >> $F
echo 'hr {clear: both}' >> $F
echo '</style></head><body>' >> $F
echo '<h1>Sentence '$S'</h1>' >> $F
echo '<p>Averages shown in squares</p>' >> $F

function AIMG () {
    I=$1
    echo '<a href="'$I'"><img border="2px solid blue" src="'$I'"></a>'
}

function IMG () {
    I=$1
    echo '<a href="'$I'"><img src="'$I'"></a>'
}

# for each layer
for l in $(seq 5 -1 0)
do
    echo '<h2>Layer '$l'</h2>' >> $F
    
    # Aggregated
    echo '<h3>Aggregated (layer '$l', sentence '$S')</h3>' >> $F
    
    # for each head
    for k in $(seq 0 $H)
    do
        IMG "s$S/k$k-l$l.png" >> $F
    done
    # average
    AIMG "s$S/kall-l$l.png" >> $F
    echo '<hr>' >> $F

    # Aggregated
    echo '<h3>Not aggregated (layer '$l', sentence '$S')</h3>' >> $F
    
    # for each head
    for k in $(seq 0 $H)
    do
        IMG "s$S/n-k$k-l$l.png" >> $F
    done
    # average
    AIMG "s$S/n-kall-l$l.png" >> $F
    echo '<hr>' >> $F
done

echo '</body></html>' >> $F

