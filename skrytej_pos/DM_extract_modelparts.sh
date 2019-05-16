#!/bin/bash

#extract_model_part_from_ckpt.py /net/projects/LSD/summarization/models/sumeczech-rnn-rnn/variables.data inpseq tagger-summeczech-rnn-rnn/embeddings.ckpt
#extract_model_part_from_ckpt.py /net/projects/LSD/summarization/models/sumeczech-rnn-rnn/variables.data encoder_text tagger-summeczech-rnn-rnn/encoder.ckpt
extract_model_part_from_ckpt.py /net/projects/LSD/sentiment/models/csfd_rnn_v2a/variables.data text_rnn_input tagger-sentiment-csfd-rnn/embeddings.ckpt
extract_model_part_from_ckpt.py /net/projects/LSD/sentiment/models/csfd_rnn_v2a/variables.data text_rnn tagger-sentiment-csfd-rnn/encoder.ckpt
extract_model_part_from_ckpt.py /net/projects/LSD/sentiment/models/csfd_rnn_san_v2a/variables.data text_rnn_input tagger-sentiment-csfd-rnn-san/embeddings.ckpt
extract_model_part_from_ckpt.py /net/projects/LSD/sentiment/models/csfd_rnn_san_v2a/variables.data text_rnn tagger-sentiment-csfd-rnn-san/encoder.ckpt


