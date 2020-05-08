from collections import defaultdict
from copy import copy
from itertools import filterfalse
from unidecode import unidecode
import pandas as pd

from tools.dependency_converter import DependencyConverter
made_directional = False

pos_labels = ('ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN','NUM',
              'PART','PRON','PROPN','PUNCT','SCONJ','SYM','VERB','X')

labels = []

label_map = {'acl': 'adj-clause',
             'advcl': 'adv-clause',
             'advmod': 'adv-modifier',
             'amod': 'adj-modifier',
             'appos': 'apposition',
             'aux': 'auxiliary',
             'xcomp': 'clausal',
             'parataxis': 'parataxis',
             'ccomp': 'clausal',
             'compound': 'compound',
             'conj': 'conjunct',
             'cc': 'cc',
             'csubj': 'clausal subject',
             'det': 'determiner',
             'nmod': 'noun-modifier',
             'nsubj': 'subject',
             'nummod': 'num-modifier',
             'obj': 'object',
             'iobj': 'object',
             'punct': 'punctuation',
             'case': 'case',
             'mark': 'mark'}

pos_map = {'ADJ': 'ADJ',
           'AUX': 'VERB',
           'DET': 'ADJ',
           'NOUN': 'NOUN',
           'NUM': 'ADJ',
           'PRON': 'NOUN',
           'PROPN': 'NOUN',
           'VERB': 'VERB'}


dep2pos_map = {#'adv-modifier' : 'ADV',
	'adj-modifier' : 'ADJ',
	'apposition' : 'NOUN',
	'auxiliary': 'VERB',
	'clausal': 'VERB',
	'compound': 'NOUN',
	'clausal subject': 'VERB',
	'determiner': 'ADJ',
	'object': 'NOUN',
	'noun-modifier': 'NOUN',
	'subject': 'NOUN',
	'num-modifier': 'ADJ'}


def define_labels(consider_directionality):
	labels_raw = list(set(label_map.values())) + ['all', 'other']
	global labels
	if consider_directionality:
		labels = [ar + '-d2p' for ar in labels_raw]
		labels.extend([ar + '-p2d' for ar in labels_raw])
	else:
		labels = labels_raw


def transform_pos(label):
	if label in pos_map:
		label = pos_map[label]
	else:
		label = 'UNK'
	return label


def transform_label2pos(label):
	if label in dep2pos_map:
		label = dep2pos_map[label]
	else:
		label = 'UNK'
	return label

def transform_label(label):
	# NOTE: version 4 when line below commented
	label = label.split(':')[0]  # to cope with nsubj:pass for instance
	if label in label_map or label + '-p2d' in label_map:
		label = label_map[label]
	else:
		label = 'other'
	
	return label


def add_dependency_relation(drs, head_id, dep_id, label, directional):
	if head_id != 0:
		label = transform_label(label)
		if directional:
			drs['all-p2d'].append((head_id, dep_id))
			drs['all-d2p'].append((dep_id, head_id))
			drs[label + '-p2d'].append((head_id, dep_id))
			drs[label + '-d2p'].append((dep_id, head_id))
		
		else:
			drs['all'].append((head_id, dep_id))
			drs['all'].append((dep_id, head_id))
			drs[label].append((head_id, dep_id))
			drs[label].append((dep_id, head_id))


def pos_dict(pos_labels):
	res_dict = dict()
	for pos1 in pos_labels:
		for pos2 in pos_labels:
			res_dict[(pos1, pos2)] = 0
	return res_dict


def conllu2ll_frame(conllu_file):
	labels2 = sorted(list(label_map.values()) + ['other', 'root'])
	ll_frame = defaultdict(dict)
	for labi in labels2:
		for labj in labels2:
			ll_frame[labi][labj] = 0
	
	if conllu_file:
		raise NotImplementedError
	
	ll_frame = pd.DataFrame.from_dict(ll_frame)
	
	return ll_frame

def conllu2pp_frame(conllu_file):
	pos_labels2 = sorted(list(set([transform_pos(l) for l in pos_labels])))
	pp_frame = defaultdict(dict)
	for posi in pos_labels2:
		for posj in pos_labels2:
			pp_frame[posj][posi] = 0
	
	if conllu_file:
		relation_labeled = read_conllu_labeled(conllu_file)
		for sent_rels in relation_labeled:
			for dep, head, label, pos in sent_rels:
				if label != 'root':
					pp_frame[transform_pos(sent_rels[head][3])][transform_pos(pos)] += 1
	
	pos_frame = pd.DataFrame.from_dict(pp_frame)
	
	return pos_frame


def conllu2freq_frame(conllu_file, directional=True):
	dependency_pos_freq = defaultdict(lambda: pos_dict(pos_labels))
	relation_labeled = read_conllu_labeled(conllu_file)
	for sent_rels in relation_labeled:
		for dep, head, label, pos in sent_rels:
			if label != 'root':
				label = transform_label(label)
				dependency_pos_freq['all-d2p'][(pos, sent_rels[head][3])] += 1
				dependency_pos_freq[label + '-d2p'][(pos, sent_rels[head][3])] += 1
				dependency_pos_freq['all-p2d'][(sent_rels[head][3], pos)] += 1
				dependency_pos_freq[label + '-p2d'][(sent_rels[head][3], pos)] += 1
	
	pos_frame = pd.DataFrame.from_dict(dependency_pos_freq)
	pos_frame = pos_frame / pos_frame.sum(axis=0)[None, :]
	pos_frame.fillna(0, inplace=True)
	
	return pos_frame.to_dict()


def conllu2dict(relations_labeled, directional=False):
	res_relations = []
	
	for sentence_rel_labeled in relations_labeled:
		sentence_rel = defaultdict(list)
		for dep, head, label, _ in sentence_rel_labeled:
			add_dependency_relation(sentence_rel, head, dep, label, directional)
		res_relations.append(sentence_rel)
	return res_relations


def read_conllu(conllu_file, directional=False):
	define_labels(directional)
	relations_labeled = read_conllu_labeled(conllu_file)
	output_relations_labeled = []
	for sent_rel in relations_labeled:
		DC = DependencyConverter(sent_rel)
		output_relations_labeled.append(DC.convert())
	relations = conllu2dict(output_relations_labeled, directional)
	return relations


def read_conllu_labeled(conllu_file):
	CONLLU_ID = 0
	CONLLU_LABEL = 7
	CONLLU_HEAD = 6
	CONLLU_POS = 3
	relations_labeled = []
	sentence_rel = []
	with open(conllu_file) as in_conllu:
		sentid = 0
		for line in in_conllu:
			if line == '\n':
				relations_labeled.append(sentence_rel)
				sentence_rel = []
				sentid += 1
			elif line.startswith('#'):
				continue
			else:
				fields = line.strip().split('\t')
				if fields[CONLLU_ID].isdigit():
					#if int(fields[CONLLU_HEAD]) != 0:
					head_id = int(fields[CONLLU_HEAD]) -1
					dep_id = int(fields[CONLLU_ID]) -1
					label = fields[CONLLU_LABEL]
					pos_tag = fields[CONLLU_POS]
					sentence_rel.append((dep_id, head_id, label, pos_tag))
	
	return relations_labeled


def read_conllu_tokens(conllu_file):
	CONLLU_ID = 0
	CONLLU_ORTH = 1
	sentence_tokens = []
	tokens = []
	with open(conllu_file) as in_conllu:
		sentid = 0
		for line in in_conllu:
			if line == '\n':
				
				tokens.append(sentence_tokens)
				sentence_tokens = []
				sentid += 1
			elif line.startswith('#'):
				continue
			else:
				fields = line.strip().split('\t')
				if fields[CONLLU_ID].isdigit():
					sentence_tokens.append(fields[CONLLU_ORTH])
	
	return tokens

# NOTE 6: fixed alignment between conllu and Bert tokenization
def group_wordpieces(wordpieces_all, conllu_file):
	'''
	Joins wordpices of tokens, so that they correspond to the tokens in conllu file.
	
	:param wordpieces_all: lists of BPE pieces for each sentence
	:param conllu_file: location of the conllu file
	:return: group_ids_all list of grouped token ids, e.g. for a BPE sentence:
	"Mr. Kowal@@ ski called" joined to "Mr. Kowalski called" it would be [[0], [1, 2], [3]]
	tokens_out_all is list of output tokens.
	'''
	grouped_ids_all = []
	tokens_out_all = []
	conllu_tokens_all = read_conllu_tokens(conllu_file)
	idx = 0
	for wordpieces, conllu_tokens in zip(wordpieces_all, conllu_tokens_all):
		conllu_id = 0
		curr_token = ''
		grouped_ids = []
		tokens_out = []
		wp_ids = []
		for wp_id, wp in enumerate(wordpieces):
			wp_ids.append(wp_id)
			if wp.endswith('@@'):
				curr_token += wp[:-2]
			else:
				curr_token += wp
			if unidecode(curr_token).lower() == unidecode(conllu_tokens[conllu_id]).lower():
				grouped_ids.append(wp_ids)
				wp_ids = []
				tokens_out.append(curr_token)
				curr_token = ''
				conllu_id += 1
		try:
			assert conllu_id == len(conllu_tokens), f'{idx} \n' \
			                                        f'bert count {conllu_id} tokens{tokens_out} \n' \
			                                        f'conllu count {len(conllu_tokens)}, tokens {conllu_tokens}'
		except AssertionError:
			grouped_ids_all.append(None)
			tokens_out_all.append([])
		else:
			tokens_out_all.append(tokens_out)
			grouped_ids_all.append(grouped_ids)
		idx += 1
	return grouped_ids_all, tokens_out_all
