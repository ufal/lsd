from collections import defaultdict
from copy import copy

labels = []

label_map = {'acl': 'clausal',
	            'advcl': 'clausal',
	            'advmod': 'modifier',
	            'amod': 'modifier',
	            'appos': 'modifier',
	            'aux': 'aux',
	            'ccomp': 'clausal',
	            'compound': 'compound',
	            'conj': 'conjunct',
	            'csubj': 'clausal',
	            'det': 'determiner',
	            'iobj': 'object',
	            'nmod': 'modifier',
	            'nsubj': 'subject',
	            'nummod': 'modifier',
	            'obj': 'object',
	            'xcomp': 'clausal'}


def define_labels(consider_directionality):
	labels_raw = list(set(label_map.values())) + ['all', 'other']
	global labels
	if consider_directionality:
		labels = [ar + '-d2p' for ar in labels_raw]
		labels.extend([ar + '-p2d' for ar in labels_raw])
	else:
		labels = labels_raw


def add_dependency_relation(drs, head_id, dep_id, label, directional):
	if head_id != 0:
		label = label.split(':')[0]  # to cope with nsubj:pass for instance
		if label in label_map or label + '-p2d' in label_map:
			label = label_map[label]
		else:
			label = 'other'
		if directional:
			drs['all-p2d'].append((head_id - 1, dep_id - 1))
			drs['all-d2p'].append((dep_id - 1, head_id - 1))
			drs[label + '-p2d'].append((head_id - 1, dep_id - 1))
			drs[label + '-d2p'].append((dep_id - 1, head_id - 1))
		
		else:
			drs['all'].append((head_id - 1, dep_id - 1))
			drs['all'].append((dep_id - 1, head_id - 1))
			drs[label].append((head_id - 1, dep_id - 1))
			drs[label].append((dep_id - 1, head_id - 1))


def read_conllu(conllu_file, directional=False):
	define_labels(directional)
	
	CONLLU_ID = 0
	CONLLU_LABEL = 7
	CONLLU_HEAD = 6
	relations = []
	sentence_rel = defaultdict(list)
	with open(conllu_file) as in_conllu:
		sentid = 0
		for line in in_conllu:
			if line == '\n':
				relations.append(sentence_rel)
				sentence_rel = defaultdict(list)
				sentid += 1
			elif line.startswith('#'):
				continue
			else:
				fields = line.strip().split('\t')
				if fields[CONLLU_ID].isdigit():
					
					if int(fields[CONLLU_HEAD]) != 0:
						add_dependency_relation(sentence_rel, int(fields[CONLLU_HEAD]), int(fields[CONLLU_ID]),
						                        fields[CONLLU_LABEL], directional)
	
	return relations
