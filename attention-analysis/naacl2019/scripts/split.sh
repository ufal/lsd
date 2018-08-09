#!/bin/bash

N=1000
NN=2000

head -n -$NN $1 > $1.train
tail -n $NN $1 | head -n $N > $1.dev
tail -n $N $1 > $1.test

