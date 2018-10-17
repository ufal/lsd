# font,size
set terminal svg size 250,250 font "Helvetica,20"
# defining box colors type 1 and 2
set linetype 1 lc rgb 'gray'
set linetype 2 lc rgb 'blue'
# with of the bars
set boxwidth 0.9
# bars should be filled with color
set style fill solid
# hide legend
set key off
# hide y axis
unset ytics
# hide the line around the graph
unset border

# should be from 0 to something above the max value
set yrange [0:60]
# the 0.6 moves the labels a bit upwards so that there is no ugly gap
set xtics nomirror scale 0 offset 0,0.5,0
# the 1.2 moves the label a bit upwards so that there is no ugly gap
set xlabel "LAS" offset 0,1,0 font "Helvetica Bold"
# output file name
set output "las-fo.svg"
# "lc variable" makes it select the box color type according to the value of the column 2
# $3+4 moves the labels somewhat upwards above the bars
plot "las-fo.tsv" using 0:3:2:xtic(1) with boxes lc variable, "" using 0:($3+9):4 with labels
