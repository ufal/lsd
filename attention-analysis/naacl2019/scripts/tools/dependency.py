from collections import defaultdict
from copy import copy
from itertools import filterfalse
from unidecode import unidecode


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
	
	if ++idx < len(sentence_relations):
		relation_map_label[idx] = 'ROOT'
		relation_map[idx] = None
		idx += 1
		
	# NOTE: version 3
	#get rid of copulas
	for idx, label in relation_map_label.items():
		if label == 'cop':
			cop_head = relation_map[idx]

			relation_map_label[idx] = relation_map_label[cop_head]
			relation_map_label[cop_head] = 'dep'

			relation_map[idx] = relation_map[cop_head]
			relation_map[cop_head] = idx

			#relation_map_reverse[cop_head].remove(idx)
			relation_map_reverse[idx].append(cop_head)
			## move some children of copula

			labels_to_move = {'nsubj', 'aux','csubj','ccomp', 'xcomp', 'advcl', 'acl', 'parataxis', 'expl','punct', 'obj'}
			for cop_dep in relation_map_reverse[cop_head]:
				if relation_map_label[cop_dep].split(':')[0] in labels_to_move:
					relation_map[cop_dep] = idx
					relation_map_reverse[idx].append(cop_dep)

			relation_map_reverse[cop_head] = list(filter(lambda x: relation_map_label[x].split(':')[0] in labels_to_move,
			                                                relation_map_reverse[cop_head]))

	# NOTE: version 5
	# expletive to subject:
	for idx, label in relation_map_label.items():
		if label == 'expl':
			expl_head = relation_map[idx]
			if idx < expl_head:
				for expl_dep in relation_map_reverse[expl_head]:
					if relation_map_label[expl_dep].split(':')[0] == 'nsubj':
						relation_map_label[expl_dep] = 'obj'
				relation_map_label[idx] = 'nsubj'

	# NOTE: version 7
	# object attends subject instead of root
	for idx, label in relation_map_label.items():
		if label == 'obj':
			obj_head = relation_map[idx]
			nsubj_idx = None
			for sibling in relation_map_reverse[obj_head]:
				if relation_map_label[sibling] == 'nsubj':
					if nsubj_idx is None:
						nsubj_idx = sibling
					else:
						nsubj_idx = None
						break
			if nsubj_idx is not None:
				relation_map[idx] = nsubj_idx
				relation_map_reverse[nsubj_idx].append(idx)
				relation_map_reverse[obj_head].remove(idx)
				
		
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
		# NOTE: version 4 when line below commented
		#label = label.split(':')[0]  # to cope with nsubj:pass for instance
		if label in label_map or label + '-p2d' in label_map:
			label = label_map[label]
		else:
			label = 'other'
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


def conllu2dict(relations_labeled, directional=False):
	res_relations = []
	
	for sentence_rel_labeled in relations_labeled:
		sentence_rel = defaultdict(list)
		for dep, head, label in sentence_rel_labeled:
			add_dependency_relation(sentence_rel, head, dep, label, directional)
		res_relations.append(sentence_rel)
	return res_relations
	
	
def read_conllu(conllu_file, directional=False):
	define_labels(directional)
	relations_labeled = read_conllu_labeled(conllu_file)
	relations_labeled = [postprocess(sent_rel) for sent_rel in relations_labeled]
	relations = conllu2dict(relations_labeled, directional)
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
	grouped_ids_all = []
	tokens_out_all = []
	conllu_tokens_all = read_conllu_tokens(conllu_file)
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
				
		assert conllu_id == len(conllu_tokens)
		tokens_out_all.append(tokens_out)
		grouped_ids_all.append(grouped_ids)
	return grouped_ids_all, tokens_out_all
