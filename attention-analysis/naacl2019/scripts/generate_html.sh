
# 1st arg = number of sentence
S=$1

F=s$S.html

echo '<!DOCTYPE html>' > $F
echo '<html><head><title>'Sentence $S'</title><style>' >> $F
echo 'img {float: left; height: 200px; width: 200px; }' >> $F
echo 'hr {clear: both}' >> $F
echo '</style></head><body>' >> $F
echo '<h1>Sentence '$S'</h1>' >> $F
echo '<p>Averages shown in red squares</p>' >> $F

function AIMG () {
    I=$1
    echo '<a href="'$I'"><img border="10px solid red" src="'$I'"></a>'
}

function IMG () {
    I=$1
    echo '<a href="'$I'"><img src="'$I'"></a>'
}

# for each layer
for l in $(seq 6 -1 1)
do
    echo '<h2>Layer '$l'</h2>' >> $F
    
    # Aggregated
    echo '<h3>Aggregated (layer '$l', sentence '$S')</h3>' >> $F
    
    # average
    AIMG "s$S/kall-l$l.png" >> $F
    # for each head
    for k in $(seq 0 15)
    do
        IMG "s$S/k$k-l$l.png" >> $F
    done

    # Aggregated
    echo '<h3>Not aggregated (layer '$l', sentence '$S')</h3>' >> $F
    
    # average
    AIMG "s$S/n-kall-l$l.png" >> $F
    # for each head
    for k in $(seq 0 15)
    do
        IMG "s$S/n-k$k-l$l.png" >> $F
    done

    echo '<hr>' >> $F
done

# for 0th layer
echo '<h2>Layer 0</h2>' >> $F
AIMG "s$S/kall-l0.png" >> $F

echo '</body></html>' >> $F

