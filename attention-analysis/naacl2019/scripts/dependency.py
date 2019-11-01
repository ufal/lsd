from collections import defaultdict
from copy import copy
from itertools import filterfalse


made_directional = False

labels = []

label_map = {'acl': 'adj-clause',
	            'advcl': 'adv-clause',
	            'advmod': 'adv-modifier',
	            'amod': 'adj-modifier',
	            'appos': 'apposition',
	            'aux': 'auxiliary',
	            'ccomp': 'clausal',
	            'compound': 'compound',
	            'conj': 'conjunct',
	            'csubj': 'clausal subject',
	            'det': 'determiner',
	            'iobj': 'i object',
	            'nmod': 'noun-modifier',
	            'nsubj': 'subject',
	            'nummod': 'num-modifier',
	            'obj': 'object',
                'punct': 'punctuation'}

def postprocess(sentence_relations):
	relation_map = dict()
	relation_map_reverse = defaultdict(list)
	relation_map_label = dict()
	idx = -1
	#print(sentence_relations)
	for rel in sentence_relations:
		idx += 1
		dep, head, label = rel
		if dep != idx:
			relation_map_label[idx] = 'ROOT'
			relation_map[idx] = None
			idx += 1
			assert idx == dep
		relation_map_label[idx] = label
		relation_map[idx] = head
		relation_map_reverse[head].append(idx)

	## get rid of copulas
	for idx, label in relation_map_label.items():
		if label == 'cop':
			cop_head = relation_map[idx]
			
			relation_map_label[idx] = relation_map_label[cop_head]
			relation_map_label[cop_head] = 'dep'
			
			relation_map[idx] = relation_map[cop_head]
			relation_map[cop_head] = idx
			
			relation_map_reverse[cop_head].remove(idx)
			relation_map_reverse[idx].append(cop_head)
			## move some children of copula
			
			labels_to_move = {'nsubj', 'aux','csubj','ccomp', 'xcomp', 'advcl', 'acl', 'parataxis', 'punct'}
			for cop_dep in relation_map_reverse[cop_head]:
				if relation_map_label[cop_dep].split(':')[0] in labels_to_move :
					relation_map[cop_dep] = idx
					relation_map_reverse[idx].append(cop_dep)
			
			relation_map_reverse[cop_head][:] = filterfalse(lambda x: x in labels_to_move ,
			                                                relation_map_reverse[cop_head])
	res_sentence_relations = []
	for idx in range(len(relation_map)):
		if relation_map[idx] is not None:
			res_sentence_relations.append((idx, relation_map[idx], relation_map_label[idx]))
	
	return res_sentence_relations

			
	


def define_labels(consider_directionality):
	labels_raw = list(set(label_map.values())) + ['all', 'other']
	global labels
	global made_directional
	if consider_directionality and not made_directional:
		labels = [ar + '-d2p' for ar in labels_raw]
		labels.extend([ar + '-p2d' for ar in labels_raw])
		made_directional = True
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


def read_conllu_labeled(conllu_file):
	CONLLU_ID = 0
	CONLLU_LABEL = 7
	CONLLU_HEAD = 6
	relations_labeled = []
	sentence_rel = []
	with open(conllu_file) as in_conllu:
		sentid = 0
		for line in in_conllu:
			if line == '\n':
				sentence_rel = postprocess(sentence_rel)
				relations_labeled.append(sentence_rel)
				sentence_rel = []
				sentid += 1
			elif line.startswith('#'):
				continue
			else:
				fields = line.strip().split('\t')
				if fields[CONLLU_ID].isdigit():
					if int(fields[CONLLU_HEAD]) != 0:
						head_id = int(fields[CONLLU_HEAD]) -1
						dep_id = int(fields[CONLLU_ID]) -1
						label = fields[CONLLU_LABEL]
						sentence_rel.append((dep_id, head_id, label))
	
	return relations_labeled
