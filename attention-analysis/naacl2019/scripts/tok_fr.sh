#!/bin/bash

# tokenizes std input to std output

export CLASSPATH=/net/projects/LSD/attention-analysis/naacl2019/scripts/stanford-parser.jar
java edu.stanford.nlp.international.french.process.FrenchTokenizer -preserveLines

