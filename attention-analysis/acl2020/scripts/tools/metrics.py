import numpy as np
from abc import abstractmethod

class Metric:
	
	@abstractmethod
	def __init__(self):
		pass
	
	@abstractmethod
	def calculate(self):
		pass
	
	
class DepAcc(Metric):
	
	def __init__(self, dependency_relations):
		self.dependency_relations = dependency_relations
	
	def calculate(self, matrices_max_in_row, relation_type):
		retrived = 0
		total = 0
		
		for index, matrix in enumerate(matrices_max_in_row):
			if matrix is not None:
				rel_pairs = self.dependency_relations[index][relation_type]
				retrived += np.sum(matrix[tuple(zip(*rel_pairs))])
				total += len(rel_pairs)
		
		if total == 0:
			return 0
		
		return retrived / total
