import numpy as np


def aggregate_subtoken_matrix(attention_matrix, wordpieces):
	# this functions connects subtokens and aggregates their attention.
	aggregate_wps = []
	wp_ids = []
	for wp_id, wp in enumerate(wordpieces):
		wp_ids.append(wp_id)
		if not wp.endswith('@@'):
			aggregate_wps.append(wp_ids)
			wp_ids = []
	
	midres_matrix = np.zeros((len(aggregate_wps), len(wordpieces)))
	
	for tok_id, wp_ids in enumerate(aggregate_wps):
		midres_matrix[tok_id, :] = np.mean(attention_matrix[wp_ids, :], axis=0)
	
	res_matrix = np.zeros((len(aggregate_wps), len(aggregate_wps)))
	
	for tok_id, wp_ids in enumerate(aggregate_wps):
		res_matrix[:, tok_id] = np.sum(midres_matrix[:, wp_ids], axis=1)
	
	words = ' '.join(wordpieces).replace('@@ ', '')
	res_tokens = words.split()
	
	assert len(res_tokens) == len(aggregate_wps), "Result matrix and token dimesnions don't match"
	return res_matrix


def generate_matrices(attentions_loaded, tokens_loaded, eos=True, no_softmax=False, maxlen=1000, sentences=None):
	sentences_count = len(tokens_loaded)
	layers_count = attentions_loaded['arr_0'].shape[0]
	heads_count = attentions_loaded['arr_0'].shape[1]
	for sentence_index in range(sentences_count):
		
		if sentences and sentence_index not in sentences:
			continue
		
		sentence_id = 'arr_' + str(sentence_index)
		tokens_count = attentions_loaded[sentence_id].shape[2]
		
		
		if eos:
			tokens_count -= 1
		tokens_list = tokens_loaded[sentence_index]
		
		# check maxlen
		words = ' '.join(tokens_list).replace('@@ ', '')
		
		words_list = words.split()
		if not len(words_list) <= maxlen:
			print('Too long sentence, skipped', sentence_index, file=sys.stderr)
			continue
		
		# NOTE sentences truncated to 64 tokens
		# assert len(tokens_list) == tokens_count, "Bad no of tokens in sent " + str(sentence_index)
		assert len(tokens_list) >= tokens_count, "Bad no of tokens in sent " + str(sentence_index)
		if len(tokens_list) > tokens_count:
			print('Too long sentence, skipped', sentence_index, file=sys.stderr)
			continue
		
		words_count = len(words_list)
		
		# for visualisation -- vis[layer][head]
		matrices = list()
		
		for layer in range(layers_count):
			layer_deps = list()  # for vis
			for head in range(heads_count):
				matrix = attentions_loaded[sentence_id][layer][head]
				if eos:
					matrix = matrix[:-1, :-1]
				# the max trick -- for each row subtract its max
				# from all of its components to get the values into (-inf, 0]
				if not no_softmax:
					matrix = matrix - np.max(matrix, axis=1, keepdims=True)
					# softmax
					exp_matrix = np.exp(matrix)
					deps = exp_matrix / np.sum(exp_matrix, axis=1, keepdims=True)
				else:
					deps = matrix / np.sum(matrix, axis=1, keepdims=True)
				deps = aggregate_subtoken_matrix(deps, tokens_list)
				layer_deps.append(deps)
			# layer_matrix = layer_matrix + deps
			matrices.append(layer_deps)
		yield matrices