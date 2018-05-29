#!/bin/bash

source /home/marecek/troja/nm/bin/activate
for i in sent-per-file/s*.txt; do
    sentnum=`echo $i | sed 's/sent-per-file\/s//;' | sed 's/\.txt//'`; \
    cat experiment-data.ini | sed "s/SENTNUM/$sentnum/g" > my-experiment-data.ini; \
    neuralmonkey/bin/neuralmonkey-run experiment.ini my-experiment-data.ini
done
rm my-experiment-data.ini
