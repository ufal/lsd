import numpy as np
import sys
from itertools import chain
from tqdm import tqdm
import multiprocessing as mp


class AttentionWrapper:
	# Those values are used in all the experiments. Parameters could be superfluous.
	MAX_LEN = 1000  # maximum number of tokens in the sentence
	WITH_EOS = True  # whether attention matrix contain EOS token.
	NO_SOFTMAX = False # whether to conduct softmax on loaded attention matrices. Should be True only for en-dev set.
	
	def __init__(self, attention_file, source_file, all_tokens_grouped):
		#loads all the attention matrices and tokens
		self.attention_loaded = np.load(attention_file)
		self.sentence_count = len(self.attention_loaded.files)
		self.layer_count = self.attention_loaded['arr_0'].shape[0]
		self.head_count = self.attention_loaded['arr_0'].shape[1]
		with open(source_file, 'r') as in_source:
			self.tokens = [l.split() for l in in_source]
			
		assert self.sentence_count == len(self.tokens), "Mismatch between the number of source sentences and " \
		                                                 "attention matrices"
		self.subtokens_grouped = all_tokens_grouped
		
	def check_subtokens(self, item):
		matrix_id = 'arr_' + str(item)
		attention_rank = self.attention_loaded[matrix_id].shape[2] - int(self.WITH_EOS)
		item_subtokens_grouped = self.subtokens_grouped[item]
		if item_subtokens_grouped is None:
			print('Token mismatch sentence skipped', item, file=sys.stderr)
			return False
		
		item_subtokens = list(chain.from_iterable(item_subtokens_grouped))
		# check maxlen
		if not len(item_subtokens_grouped) <= self.MAX_LEN:
			print('Too long sentence, skipped', item, file=sys.stderr)
			return False
		# NOTE sentences truncated to 64 tokens
		if len(item_subtokens) != attention_rank:
			print('Too long sentence, skipped', item, file=sys.stderr)
			return False
		return True
	
	@staticmethod
	def aggregate_subtoken_matrix(attention_matrix, tokens_grouped):
		# this functions connects subtokens and aggregates their attention.
		midres_matrix = np.zeros((len(tokens_grouped), attention_matrix.shape[0]))
		
		for tok_id, wp_ids in enumerate(tokens_grouped):
			midres_matrix[tok_id, :] = np.mean(attention_matrix[wp_ids, :], axis=0)
		
		res_matrix = np.zeros((len(tokens_grouped), len(tokens_grouped)))
		
		for tok_id, wp_ids in enumerate(tokens_grouped):
			res_matrix[:, tok_id] = np.sum(midres_matrix[:, wp_ids], axis=1)
		
		return res_matrix
	
	def get_head(self, item, layer_id, head_id, tokens_checked=False, argmax_in_row=False):
		matrix_id = 'arr_' + str(item)
		if not tokens_checked and not self.check_subtokens(item):
			return None
		
		matrix = self.attention_loaded[matrix_id][layer_id][head_id]
		if self.WITH_EOS:
			matrix = matrix[:-1, :-1]
		# the max trick -- for each row subtract its max
		# from all of its components to get the values into (-inf, 0]
		if not self.NO_SOFTMAX:
			matrix = matrix - np.max(matrix, axis=1, keepdims=True)
			exp_matrix = np.exp(matrix)
			matrix = exp_matrix / np.sum(exp_matrix, axis=1, keepdims=True)
		else:
			matrix = matrix / np.sum(matrix, axis=1, keepdims=True)
		matrix = self.aggregate_subtoken_matrix(matrix, self.subtokens_grouped[item])
		if argmax_in_row:
			matrix = (matrix == matrix.max(axis=1)[:, None]).astype(int)
		return matrix
	
	def calc_metric(self, metric, params, selected_sentences=None):
		metric_res = dict()
		if selected_sentences is None:
			selected_sentences = range(self.sentence_count)
			
		#selected_sentences = (s for s in selected_sentences if self.check_subtokens(s))
		matrices = [[(self.get_head(s, l, h, argmax_in_row=True) for s in selected_sentences)
		             for h in range(self.head_count)] for l in range(self.layer_count)]
		for p in tqdm(params):
			metric_res[p] = np.zeros((self.layer_count, self.head_count))
			metric_res[p] = np.array([[metric.calculate(matrices[l][h], p) for h in range(self.head_count)]
			                          for l in range(self.layer_count)])
			
		return metric_res
	
	def __getitem__(self, item):
		matrix_id = 'arr_' + str(item)
		matrices = []
		if not self.check_subtokens(item):
			return None
		for layer_id in range(self.layer_count):
			layer_matrices = [self.get_head(item,layer_id,head_id,tokens_checked=True) for
			                  head_id in range(self.head_count)]
			matrices.append(layer_matrices)
		
		return matrices
	
	def __iter__(self):
		for item in range(self.sentence_count):
			yield self.__getitem__(item), item
		

