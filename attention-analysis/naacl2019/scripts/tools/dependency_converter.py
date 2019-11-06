from collections import defaultdict
from itertools import filterfalse


class DependencyConverter:

	def __init__(self, sentence_relations):
		self.to_head = dict()
		self.to_deps = defaultdict(list)
		self.to_label = dict()
		idx = -1
		# print(sentence_relations)
		for rel in sentence_relations:
			idx += 1
			dep, head, label = rel
			if dep != idx:
				self.to_label[idx] = 'ROOT'
				self.to_head[idx] = -1
				self.to_deps[-1].append(idx)
				idx += 1
				assert idx == dep
			self.to_label[idx] = label
			self.to_head[idx] = head
			self.to_deps[head].append(idx)
		
		if ++idx < len(sentence_relations):
			self.to_label[idx] = 'ROOT'
			self.to_head[idx] = -1
			self.to_deps[-1].append(idx)
			idx += 1
		
	def __change_direction(self, old_dep, new_label):
		old_head = self.to_head[old_dep]
		self.__change_label(old_dep, self.to_label[old_head])
		self.__change_label(old_head, new_label)
		
		self.to_deps[self.to_head[old_head]].remove(old_head)
		self.to_deps[self.to_head[old_head]].append(old_dep)
		
		self.to_deps[old_head].remove(old_dep)
		self.to_deps[old_dep].append(old_head)
		
		
		self.to_head[old_dep] = self.to_head[old_head]
		self.to_head[old_head] = old_dep
		
		return old_head
		
	def __move_labeled_relations(self, old_head, new_head, labels_to_move):
		for old_heads_dep in self.to_deps[old_head]:
			if self.to_label[old_heads_dep].split(':')[0] in labels_to_move:
				self.to_head[old_heads_dep] = new_head
				self.to_deps[new_head].append(old_heads_dep)
		
		self.to_deps[old_head] = \
			list(filterfalse(lambda x: self.to_label[x].split(':')[0] in labels_to_move,
			                 self.to_deps[old_head]))
		
	def __change_label(self, dep, new_label):
		self.to_label[dep] = new_label
		
	def __change_dependent_labels(self, head, label_map):
		for dep in self.to_deps[head]:
			if self.to_label[dep].split(':')[0] in label_map:
				self.to_label[dep] = label_map[self.to_label[dep].split(':')[0]]
		
	def __move_relation(self, dep, new_head, new_label):
		old_head = self.to_head[dep]
		
		self.to_head[dep] = new_head
		self.to_deps[old_head].remove(dep)
		self.to_deps[new_head].append(dep)
		
		self.__change_label(dep, new_label)
		
	def check_structure(self):
		for dep_id, head_id in self.to_head.items():
			assert dep_id in self.to_deps[head_id]
			assert dep_id in self.to_label
	
	# NOTE: version 3
	# get rid of copulas
	def remove_copulas(self):
		copulas = []
		labels_to_move = {'nsubj', 'aux', 'csubj', 'ccomp', 'xcomp', 'advcl', 'acl', 'parataxis', 'expl',
		                  'punct', 'obj'}
		for idx, label in self.to_label.items():
			if label == 'cop':
				copulas.append(idx)
		
		for copula_dep in copulas:
			new_dep = self.__change_direction(copula_dep, 'dep')
			self.check_structure()
			self.__move_labeled_relations(new_dep, copula_dep, labels_to_move)
			self.check_structure()
	
	# NOTE: version 5
	# expletive to subject:
	def expletive2subject(self):
		expletives = []
		for idx, label in self.to_label.items():
			# only change when expletive dependent is before head in sentence
			if label == 'expl' and idx < self.to_head[idx]:
				expletives.append(idx)
				
		for expl_dep in expletives:
			self.__change_dependent_labels(self.to_head[expl_dep], {'obj': 'nsubj'})
			self.__change_label(expl_dep, 'nsubj')
	
	# NOTE: version 7
	# object attends subject instead of root
	def object2subject_attachment(self):
		
		objects = []
		for idx, label in self.to_label.items():
			if label == 'obj':
				objects.append(idx)
				
		for obj_dep in objects:
				obj_head = self.to_head[obj_dep]
				
				# at most one subject in sentence
				nsubj_dep = None
				for sibling in self.to_deps[obj_head]:
					if self.to_label[sibling] == 'nsubj':
						if nsubj_dep is None:
							nsubj_dep = sibling
						else:
							nsubj_dep = None
							break
				if nsubj_dep is not None:
					self.__move_relation(obj_dep,nsubj_dep, 'obj')
	
	def convert(self):
		self.check_structure()
		self.remove_copulas()
		self.check_structure()
		self.expletive2subject()
		self.check_structure()
		self.object2subject_attachment()
		self.check_structure()
		res_sentence_relations = []
		for idx in range(len(self.to_head)):
			if self.to_head[idx] is not None:
				res_sentence_relations.append((idx, self.to_head[idx], self.to_label[idx]))
		
		return res_sentence_relations