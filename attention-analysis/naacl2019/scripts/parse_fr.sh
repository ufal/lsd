#!/usr/bin/env bash
#
# Defines standard configurations for parsing with the
# multilingual parsers (Arabic, Chinese, German, French). 
#
# For English, it is easier to use lexparser.sh, although you can load 
# an English grammar with this script.
#
# For details on the language-specific options, see the javadocs and
# lexparser_lang.def.
#

# Memory limit
mem=5g

#Maximum length of the sentences to parse
len=128

# Language-specific configuration

# French
lang=French
tlp=edu.stanford.nlp.parser.lexparser.FrenchTreebankParserParams
lang_opts="-frenchFactored -encoding UTF-8"
grammar=frenchFactored.ser.gz

# Setting classpath
scriptdir=/net/projects/LSD/attention-analysis/naacl2019/stanford-parser-full-2018-02-27
CLASSPATH="$CLASSPATH":"$scriptdir/*"

#Prefix for the output filename'
# -outputFilesExtension "$out_file"."$len".stp \

# Run the Stanford parser
java -Xmx"$mem" -cp "$CLASSPATH" edu.stanford.nlp.parser.lexparser.LexicalizedParser -maxLength "$len" \
-tLPP "$tlp" $lang_opts $parse_opts -writeOutputFiles \
-sentences newline -outputFormat "penn" \
-outputFormatOptions "removeTopBracket,includePunctuationDependencies" -loadFromSerializedFile $grammar $*

