#!/usr/bin/env python3

# Licence: CC-BY 3.0
# Authors: David Mareček <marecek@ufal.mff.cuni.cz>, Rudolf Rosa <rosa@ufal.mff.cuni.cz>

import numpy as np
import codecs
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nltk import Tree
import random
import math
import subprocess
import sys
from collections import deque, Counter, defaultdict
from scipy.sparse.csgraph import minimum_spanning_tree
import string

ap = argparse.ArgumentParser()
ap.add_argument("-a", "--attentions", required=True,
        help="NPZ file with attentions")
ap.add_argument("-t", "--tokens", required=True,
        help="Labels (tokens) separated by spaces")
ap.add_argument("-d", "--deptrees",
        help="Output unori dep trees into this file")
ap.add_argument("-o", "--oritrees",
        help="Output oriented dep trees into this file")
ap.add_argument("-p", "--phrasetrees",
        help="Output phrase trees into this file")
ap.add_argument("--tikz", action="store_true",
        help="Output Tikz trees")
ap.add_argument("-v", "--visualizations",
        help="Output heatmap prefix")
ap.add_argument("-f", "--format", default="png",
        help="Output visualisation as this format (pdf, png, maybe other options)")
ap.add_argument("-F", "--fontsize", default=8, type=int,
        help="Fontsize for heatmap; 8 is good for png. 10 is good for PDF it seems")
ap.add_argument("--colmax",
        help="Output stats of how often words are looked at into this file")
ap.add_argument("-c", "--conllu",
        help="Eval against the given conllu faile")
ap.add_argument("-C", "--phrasesfile",
        help="Eval against the given Staford phrases faile")
ap.add_argument("-b", "--baseline",
        help="Eval baseline: rbr/lbr/rbin/lbin/rand")
ap.add_argument("-r", "--reverse", action="store_true",
        help="Reverse mode of evaluation")

ap.add_argument("-w", "--phraseweights",
        help="Visualise weights of individual phrases")

ap.add_argument("-l", "--layer", type=int, default=-1,
        help="Only use the specified layer; 0-based")
ap.add_argument("-k", "--head", type=int, default=-1,
        help="Only use the specified head from the last layer; 0-based")
ap.add_argument("-K", "--heads", type=str,
        help="layer-head,layer-head,... use only these (0-based)")
ap.add_argument("-s", "--sentences", nargs='+', type=int, default=[4,5,6],
        help="Only use the specified sentences; 0-based")
ap.add_argument("-m", "--maxlen", type=int, default=1000,
        help="Skip sentences longer than this many words. A word split into several wordpieces is counted as one word. EOS is not counted.")

#ap.add_argument("-V", "--verbose", action="store_true",
#        help="Print more details")
ap.add_argument("-B", "--balustradeness", action="store_true",
        help="Compute how much balustrady each head is")
ap.add_argument("-D", "--sentences_as_dirs", action="store_true",
        help="Store images into separate directories for each sentence")
ap.add_argument("-e", "--eos", action="store_true",
        help="Attentions contain EOS")
ap.add_argument("-n", "--noaggreg", action="store_true",
        help="Do not aggregate the attentions over layers, just use one layer")
ap.add_argument("-P", "--nopunct", action="store_true",
        help="Remove punctuation before evaluation")
args= ap.parse_args()

layerheads = None
if args.heads:
    layerheads = defaultdict(list)
    for lh in args.heads.split(','):
        if lh != '':
            layer, head = lh.split('-')
            layerheads[int(layer)].append(int(head))

# weights[i][j] = word_mixture[6][i][j] = attention weight
# wordpieces = list of tokens
def deptree(weights, wordpieces):
    size = len(wordpieces)
    graph = [ [0] * size for i in range(size)  ]
    for brother in range(size-1):
        for sister in range(brother+1, size-1):
            for row in range(size):
                # MINIMUM spanning tree
                # now sum
                # TODO max
                score = - weights[row][brother] * weights[row][sister]
                graph[brother][sister] += score

    mst = minimum_spanning_tree(graph).toarray()

    lines = []
    for brother in range(size-1):
        sisters = []
        for sister in range(brother+1, size-1):
            if mst[brother][sister] != 0 or mst[sister][brother] != 0:
                sisters.append(str(sister))
        # 5    the_    3,4,6
        lines.append('\t'.join((
            str(brother), wordpieces[brother], ','.join(sisters)
        )))

    # end of sentence
    lines.append('')

    return '\n'.join(lines)

def oritree(weights, wordpieces):
    size = len(wordpieces)

    # non-optimal greedy MST algorithm
    heads = dict()
    headweights = dict()
    nodes = set(range(size))
    # find root node
    root = np.argmax(np.diag(weights))
    heads[root] = -1
    headweights[root] = weights[root][root]
    nodes.remove(root)
    # construct tree
    while nodes:
        # find best child to attach into the partial tree
        best_weight = -1
        best_parent = -1
        best_child  = -1
        # children = not yet attached nodes
        for child in nodes:
            # parents = already attached nodes
            for parent in heads.keys():
                weight = weights[child][parent]
                if weight > best_weight:
                    best_weight = weight
                    best_child  = child
                    best_parent = parent
        # attach best child
        assert best_child != -1
        heads[best_child] = best_parent
        headweights[best_child] = best_weight
        nodes.remove(best_child)
    # conll-like output
    lines = []
    for child in range(size):
        # 5    the_    3
        lines.append('\t'.join((
            str(child + 1),
            wordpieces[child],
            str(heads[child] + 1),
            str(round(headweights[child], 2)),
            wordpieces[heads[child]],
        )))
    # end of sentence
    lines.append('')

    return '\n'.join(lines)

def parse_subtree(i, j, phrase_weight, wordpieces):
    
    if (i == j):
        if args.tikz:
            return wordpieces[i]
        #return str(i) + ':' + wordpieces[i]
        else:
            return i
        #return Tree(wordpieces[i], [i])
    
    best_k = i
    maximum = 0
    for k in range(i, j):
        value = phrase_weight[i][k] + phrase_weight[k + 1][j]
        if value > maximum:
            maximum = value
            best_k = k
    subtree1 = parse_subtree(i, best_k, phrase_weight, wordpieces)
    subtree2 = parse_subtree(best_k + 1, j, phrase_weight, wordpieces)
    return Tree('X:'+str(round(maximum/(j-i+1),2)), [subtree1, subtree2])
    
def cky(phrase_weight, wordpieces):
    # CKY on wordpieces
    size = len(wordpieces)
    ctree = [[0 for i in range(size)] for j in range(size)]
    score = np.zeros((size, size))
    for i in range(size):
        if args.tikz:
            ctree[i][i] = wordpieces[i]
        else:
            ctree[i][i] = i
        score[i][i] = 0.5
    for span in range(1, size):
        for pos in range(0, size):
            if (pos + span < size):
                best_score = -1
                best_variant = 0
                for variant in range(1, span + 1):
                    var_score = (  phrase_weight[pos][pos + span - variant] \
                                 + score[pos][pos + span - variant] \
                                 + phrase_weight[pos + span - variant + 1][pos + span] \
                                 + score[pos + span - variant + 1][pos + span] \
                                ) / 4 
                    if (best_score < var_score):
                        best_score = var_score
                        best_variant = variant
                score[pos][pos + span] = best_score
                ctree[pos][pos + span] = Tree('X', [ctree[pos][pos + span - best_variant], ctree[pos + span - best_variant + 1][pos + span]])
    return ctree[0][size - 1]

def colmaxes(vis, wordpieces):
    # init
    wordpieces_counts = Counter(wordpieces)
    result = dict();
    for w in wordpieces_counts:
        result[w] = 0;
    # record
    layers_count = len(vis)
    heads_count = len(vis[0][0])
    tokens_count = len(wordpieces)
    for l in range(layers_count):
        for h in range(heads_count):
            argmax_in_row = np.argmax(vis[l][0][h] - np.diagflat(np.ones(tokens_count)), axis=1)
            for i in argmax_in_row:
                result[wordpieces[i]] += 1
    # normalize
    divisor = layers_count * heads_count
    for w in wordpieces_counts:
        result[w] /= divisor * wordpieces_counts[w]
    # return
    return result

def phrasetree(vis, wordpieces, layer, aggreg, head, sentence_index):
    size = len(wordpieces)
    layer_list = range(len(vis))
    if layer != -1:
        layer_list = [layer]
    if layerheads:
        layer_list = list(layerheads.keys())
    head_list = range(len(vis[layer][0]))
    if head != -1:
        head_list = [head]
    phrase_weight = np.zeros((size, size))
    # iterate over all layers
    for l in layer_list:
        if layerheads != None:
            head_list = layerheads[l]
        for h in head_list:
            # save a maximum value for each row, except the diagonal
            #max_in_row = np.max(vis[l][aggreg][h] - np.diagflat(np.ones(size)), axis=1) # ORIGINAL
            #vis[l][aggreg][h] -= 0.5 * np.diagflat(np.ones(size))                        # ALTERNATIVE
            max_in_row = np.max(vis[l][aggreg][h], axis=1)                               # ALTERNATIVE
            #print(np.round(vis[l][aggreg][h],1))
            #print(np.round(vis[l][aggreg][h] - np.diagflat(np.ones(size)),1))
            #print(np.round(max_in_row,1))
            for column in range(size):
                i = 0
                while i < size:
                    current_sum = 0
                    for j in range(i, size):
                        value = vis[l][aggreg][h][j][column]
                        if value < max_in_row[j]:
                        #if value < 0.2:
                        #if value < 0.1:
                            j -= 1
                            break
                        current_sum += value
                    if j >= i:
                        pw = current_sum / (j - i + 1)
                        #if (phrase_weight[i][j] < pw):
                        #    phrase_weight[i][j] = pw
                        phrase_weight[i][j] += pw
                    i = j + 2

    # normalize phrase_weight, so that the mean on each diagonal is 0.5
    for span in range(size):
        factor = 0
        count = 0
        for i in range(size - span):
            if (phrase_weight[i][i + span] > 0):
                factor += phrase_weight[i][i + span]
                count += 1
        if (count > 0):
            factor = factor / count * 2
            for i in range(size - span):
                if (factor != 0):
                    phrase_weight[i][i + span] /= factor

    #print(phrase_weight)
    #print(np.round(phrase_weight,1))
    # parse the tree recursively in top-down fashion
    #tree = parse_subtree(0, size - 1, phrase_weight, wordpieces)
    
    if (args.phraseweights):
        filename = args.phraseweights + "-s" + str(sentence_index) + ".png"
        heatmap(phrase_weight, "", "", "", tokens_list, tokens_list)
        plt.savefig(filename, dpi=200, format='png', bbox_inches='tight')
        plt.close()
    
    # parse tree using CKY
    tree = cky(phrase_weight, wordpieces)

    return(tree)
                        
def baselinephrasetree(wordpieces, baselinetype):
    tree = None
    size = len(wordpieces)
    if baselinetype == 'lbr':
        tree = 0
        for index in range(1, size):
            tree = Tree('X', [tree, index])
    elif baselinetype == 'rbr':
        tree = size-1
        # go from penultimate to 0th
        for index in range(size-2, -1, -1):
            tree = Tree('X', [index, tree])
    elif baselinetype == 'lbin':
        pieces = range(0, size)
        while len(pieces) > 1:
            newpieces = []
            for i in range(0, len(pieces)-1, +2):
                newpieces.append(Tree('X', [pieces[i], pieces[i+1]]))
            if len(pieces)%2 == 1:
                newpieces.append(pieces[-1])
            pieces = newpieces
        tree = pieces[0]
    elif baselinetype == 'rbin':
        pieces = range(size-1, -1, -1)
        while len(pieces) > 1:
            newpieces = []
            for i in range(0, len(pieces)-1, +2):
                newpieces.append(Tree('X', [pieces[i], pieces[i+1]]))
            if len(pieces)%2 == 1:
                newpieces.append(pieces[-1])
            pieces = newpieces
        tree = pieces[0]
    else:
        assert False, 'unknown baseline type ' + baselinetype
    return tree

def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels):
    '''
    Copied form:
    https://stackoverflow.com/questions/20574257/constructing-a-co-occurrence-matrix-in-python-pandas
    '''
    # Plot it out
    fig, ax = plt.subplots()    
    c = ax.pcolor(AUC, edgecolors='k', linestyle= 'dashed', linewidths=0.2, cmap='pink', vmin=0.0, vmax=1.0)
    
    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(AUC.shape[0]) + 0.5, minor=False)
    ax.set_xticks(np.arange(AUC.shape[1]) + 0.5, minor=False)
    
    # set tick labels
    xfont = {'family': 'serif', 'weight': 'normal', 'size': args.fontsize, 'rotation' : 'vertical'}
    yfont = {'family': 'serif', 'weight': 'normal', 'size': args.fontsize}
    #ax.set_xticklabels(np.arange(1,AUC.shape[1]+1), minor=False)
    ax.set_xticklabels(xticklabels, minor=False, fontdict=xfont)
    ax.set_yticklabels(yticklabels, minor=False, fontdict=yfont)
    
    # set title and x/y labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)      

    # Remove last blank column
    plt.xlim( (0, AUC.shape[1]) )

    # Turn off all the ticks
    ax = plt.gca()    
    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False

    # Add color bar
    plt.colorbar(c)

    # Add text in each cell 
    #show_values(c)

    # Proper orientation (origin at the top left instead of bottom left)
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    # resize 
    fig = plt.gcf()
    #fig.set_size_inches(cm2inch(40, 20))


def write_heatmap(tokens_list, sentence_index, vis, layer, aggreg, head=-1):
    filename = ''
    filename += args.visualizations
    filename += "s" + str(sentence_index)
    if args.sentences_as_dirs:
        filename += "/"
    else:
        filename += "-"
    if aggreg == 0:
        filename += 'n-'
    if head == -1:
        filename += 'kall-'
    else:
        filename += 'k' + str(head) + '-'
    filename += 'l' + str(layer)
    filename += '.' + args.format

    heatmap(vis[layer][aggreg][head], "", "", "", tokens_list, tokens_list)
    plt.savefig(filename, dpi=200, format=args.format, bbox_inches='tight')
    plt.close()

# map 1-based word-based conllu token IDs
# to 0-based wordpiece-based indices
def tokens2wordpieces_map(wordpieces):
    token_index = 0
    wordpiece_index = -1
    token2wordpiece = dict()
    for wordpiece in wordpieces:
        wordpiece_index += 1
        if wordpiece.endswith('@@'):
            pass
        else:
            token_index += 1
            token2wordpiece[token_index] = wordpiece_index
    return token2wordpiece

#load data
attentions_loaded = np.load(args.attentions)
sentences_count = len(attentions_loaded.files)
layers_count = attentions_loaded['arr_0'].shape[0]
heads_count = attentions_loaded['arr_0'].shape[1]
with open(args.tokens) as tokens_file:
    tokens_loaded = [l.split() for l in tokens_file]
if args.conllu != None:
    CONLLU_ID = 0
    CONLLU_HEAD = 6
    with open(args.conllu) as conllu_file:
        conllu = list()
        sentence = None
        sentid = 0
        for line in conllu_file:
            if line == '\n':
                if args.eos:
                    # add EOS
                    end = max(sentence)
                    sentence[end+1] = end
                conllu.append(sentence)
                sentence = None
                sentid += 1
            elif line.startswith('#'):
                continue
            else:
                if sentence == None:
                    sentence = dict()
                    token2wordpiece = tokens2wordpieces_map(tokens_loaded[sentid])

                fields = line.strip().split('\t')
                if fields[CONLLU_ID].isdigit():
                    child = token2wordpiece[int(fields[CONLLU_ID])]
                    head = int(fields[CONLLU_HEAD])
                    if head == 0:
                        # root
                        head = -1
                    else:
                        head = token2wordpiece[head]
                    sentence[child] = head
                # else special token -- continue

if args.balustradeness:
    balustradeness = [ [0 for head in range(heads_count)]
            for layer in range(layers_count) ]

def wsjlen(wordpiece):
    if wordpiece in ['(', ')', '[', ']', '{', '}']:
        # -RRB- et al.
        result = 5
    elif wordpiece.endswith('@@'):
        # strip boundary mark
        result = len(wordpiece) - 2
    else:
        result = len(wordpiece)
    return result

def brackets2tree(sentence_string, tokens_list):
    sentence_string = sentence_string.replace(')', ' )')
    wsj_tokens = sentence_string.split()
    queue = [ Tree('TOOR', []) ]
    cur_token = 0
    skip_len = 0
    for wsj_token in wsj_tokens:
        if wsj_token.startswith('('):
            # start a new subphrase
            p = Tree(wsj_token[1:], [])
            queue[-1].append(p)
            queue.append(p)
        elif wsj_token == ')':
            # end the current subphrase
            p = queue.pop()
            if len(p) == 0:
                # remove empty phrase
                queue[-1].pop()
        else:
            #print('WSJ', wsj_token, file=sys.stderr)
            # add token(s) into subphrase
            if skip_len > 0:
                skip_len -= len(wsj_token)
            else:
                l = 0
                while l < len(wsj_token):
                    #print('APP', tokens_list[cur_token], file=sys.stderr)
                    queue[-1].append(cur_token)
                    l += wsjlen(tokens_list[cur_token])
                    cur_token += 1
                if l > len(wsj_token):
                    skip_len = l - len(wsj_token)
                if args.eos and cur_token+1 == len(tokens_list):
                    # we have reached EOS
                    queue[-1].append(cur_token)
    assert len(queue) == 1
    return queue[0][0]
    
# read in gold prase structure parse trees
if args.phrasesfile != None:
    gold_phrasetrees = list()
    sent_id = 0
    sentence_string = list()
    with open(args.phrasesfile) as infile:
        for line in infile:
            if line == '\n':
                gold_phrasetrees.append(''.join(sentence_string))
                sent_id += 1
                sentence_string = list()
            else:
                sentence_string.append(line)

# outputs
if args.deptrees:
    deptrees = open(args.deptrees, 'w')
else:
    deptrees = None
if args.oritrees:
    oritrees = open(args.oritrees, 'w')
else:
    oritrees = None
if args.phrasetrees:
    phrasetrees = open(args.phrasetrees, 'w')
else:
    phrasetrees = None
if args.colmax:
    colmaxfile = open(args.colmax, 'w')
else:
    colmaxfile = None

# recursively aggregated -- attention over input tokens
def wm_aggreg(this_layer, last_layer):
    return (np.matmul(this_layer, last_layer) + last_layer) / 2

# this layer and residual connection -- attention over positions
def wm_avg(this_layer, first_layer):
    return (this_layer + first_layer) / 2

def del_punct_from_phrase(phrase, tokens_list):
    new_children = list()
    for old_child in phrase:
        if type(old_child) == int:
            # terminal -- check to remove punct
            if not ispunct(tokens_list[old_child]):
                new_children.append(old_child)
                # else remove
        else:
            # non-terminal -- recurse
            new_child = del_punct_from_phrase(old_child, tokens_list)
            if new_child != None:
                new_children.append(new_child)
                # else remove
    
    phrase.clear()
    if len(new_children) >= 2:
        phrase.extend(new_children)
        return phrase
    elif len(new_children) == 1:
        return new_children[0]
    else:
        assert len(new_children) == 0
        return None
        

# TODO
# if args.nopunct
# recursively go through each tree, delete int nodes that are punct
# recursively go through each tree, compress phrases with only 1 child, delete
# empty phrases (need to do that bottom up; maybe can be done in one pass but
# easier to think up in two)
def eval_phrase_tree(gold_tree, predicted_tree, tokens_list):
    count_phrases = 0
    count_good = 0

    if args.nopunct:
        gold_tree = del_punct_from_phrase(gold_tree, tokens_list)                
        predicted_tree = del_punct_from_phrase(predicted_tree, tokens_list)                
    if gold_tree == None or type(gold_tree) == int:
        return (0, 0)
    
    gold_spans = list()
    queue = deque()
    queue.append(gold_tree)
    while queue:
        phrase = queue.popleft()
        if len(phrase) > 1:
            # ignore trivial phrases
            span = phrase.leaves()
            start = min(span)
            end = max(span)
            gold_spans.append((start, end))
        for subphrase in phrase:
            if type(subphrase) != int:
                queue.append(subphrase)
    
    queue = deque()
    queue.append(predicted_tree)
    while queue:
        phrase = queue.popleft()
        if len(phrase) > 1:
            # ignore trivial phrases
            count_phrases += 1
            good = True
            span = phrase.leaves()
            start = min(span)
            end = max(span)
            for gold_span in gold_spans:
                gold_start = gold_span[0]
                gold_end = gold_span[1]
                if start <= gold_end and gold_start <= end:
                    # they overlap
                    if start < gold_start and end < gold_end:
                        good = False
                    if start > gold_start and end > gold_end:
                        good = False
            if good:
                count_good += 1
            print(start, tokens_list[start], '...', end, tokens_list[end],
                    ':', good, file=sys.stderr)
        # recurse
        for subphrase in phrase:
            if type(subphrase) != int:
                queue.append(subphrase)
    return (count_phrases, count_good)

def ispunct(word):
    return all(x in string.punctuation for x in word) or word == 'EOS'

# eval
total_count_phrases = 0
total_count_good = 0
total_sum_scores = 0
total_count_sentences = 0

colmaxes_all = dict()

# iterate over sentences
for sentence_index in range(sentences_count):
    # option to only process selected sentences
    if args.sentences and sentence_index in args.sentences:
        pass
    else:
        continue
    
    sentence_id = 'arr_' + str(sentence_index)
    tokens_count = attentions_loaded[sentence_id].shape[2]
    tokens_list = tokens_loaded[sentence_index]
    
    # check maxlen
    words = ' '.join(tokens_list).replace('@@ ', '')
    if args.nopunct:
        words = words.translate(str.maketrans("", "", string.punctuation))
    words_list = words.split()
    if len(words_list) <= args.maxlen:
        print('Processing sentence', sentence_index, file=sys.stderr)
    else:
        continue
        
    if args.eos:
        tokens_list.append('EOS')
    # NOTE sentences truncated to 64 tokens
    # assert len(tokens_list) == tokens_count, "Bad no of tokens in sent " + str(sentence_index)
    assert len(tokens_list) >= tokens_count, "Bad no of tokens in sent " + str(sentence_index)
    if len(tokens_list) > tokens_count:
        TRUNCATED = True
        print('Truncating tokens from ', len(tokens_list), 'to', tokens_count,
                'on line', sentence_index, '(0-based indexing)', file=sys.stderr)
        tokens_list = tokens_list[:tokens_count]
    else:
        TRUNCATED = False


    # recursively compute layer weights
    word_mixture = list() 
    word_mixture.append(np.identity(tokens_count))
    # for visualisation -- vis[layer][aggreg][head]
    vis = list()
    for layer in range(layers_count):
        layer_deps = list()  # for vis
        layer_matrix = np.zeros((tokens_count, tokens_count))
        for head in range(heads_count):
            matrix = attentions_loaded[sentence_id][layer][head]
            # the max trick -- for each row subtract its max
            # from all of its components to get the values into (-inf, 0]            
            matrix = np.transpose(np.transpose(matrix) - np.max(matrix, axis=1))
            # softmax
            exp_matrix = np.exp(matrix)
            deps = np.transpose(np.transpose(exp_matrix) / np.sum(exp_matrix, axis=1))
            layer_deps.append(deps)
            layer_matrix = layer_matrix + deps
        # avg
        layer_matrix = layer_matrix / heads_count
        layer_deps.append(layer_matrix)
        # next layer = avg of this layer and prev layer
        # TODO add head weights from ff matrices
        vis.append([
                #[wm_avg(m, word_mixture[0]) for m in layer_deps],
                layer_deps,
                [wm_aggreg(m, word_mixture[layer]) for m in layer_deps],
                ])
        word_mixture.append( wm_aggreg(layer_matrix, word_mixture[layer]) )

        #if sentence_index == 6:
           #print("LM")
           #print(layer_matrix)
           #print("WM")
           #print(word_mixture[-1])

    if args.balustradeness:
        for layer in range(layers_count):
            for head in range(heads_count):
                b = 0
                for column in range(tokens_count):
                    for row in range(tokens_count-1):
                        b += vis[layer][0][head][row][column] * vis[layer][0][head][row+1][column]
                balustradeness[layer][head] += b/(tokens_count+1)
                #balustradeness[layer][head] += b/tokens_count/(tokens_count-1)
                #balustradeness[layer][head] = b

    # compute trees
    if deptrees:
        # print("Deptrees disabled!", file=sys.stderr)
        # tree = deptree(np.transpose(word_mixture[-1]), tokens_list)
        aggreg = 0 if args.noaggreg else 1
        tree = deptree(vis[args.layer][aggreg][args.head], tokens_list)
        print(tree, file=deptrees)

    if oritrees:
        # print("Deptrees disabled!", file=sys.stderr)
        # tree = deptree(np.transpose(word_mixture[-1]), tokens_list)
        aggreg = 0 if args.noaggreg else 1
        tree = oritree(vis[args.layer][aggreg][args.head], tokens_list)
        print(tree, file=oritrees)

    if args.colmax:
        print("COLMAXES", file=colmaxfile)
        colmaxes_dict = colmaxes(vis, tokens_list)
        for w in tokens_list:
            c = 10 * colmaxes_dict[w]
            print("{:4.1f} {}".format(c, w), file=colmaxfile)
            if w in colmaxes_all:
                ratio, count = colmaxes_all[w]
                colmaxes_all[w] = (ratio+c, count+1)
            else:
                colmaxes_all[w] = (c, 1)
        print(file=colmaxfile)
        for i in reversed(np.argsort(list(colmaxes_dict.values()))):
            print("    " * i, i, tokens_list[i], file=colmaxfile)


    if phrasetrees:
        aggreg = 0 if args.noaggreg else 1
        if args.baseline != None:
            tree = baselinephrasetree(tokens_list, args.baseline)
        else:
            tree = phrasetree(vis, tokens_list, args.layer, aggreg, args.head, sentence_index)
        #print(str(tree), file=phrasetrees)
        #for subtree in tree.subtrees():
        #    print(" ".join(subtree.leaves()), file=phrasetrees)
        #print("", file=phrasetrees)
        #tree.draw()
        #tree.pretty_print(stream=phrasetrees)
        if args.tikz:
            t = str(tree)
            t = t.replace('(', '[').replace(')', ' ]').replace('X', '.X')
            print(t, file=phrasetrees)
        else:
            tree.pretty_print(stream=phrasetrees, sentence=tokens_list)
            tree.pretty_print(stream=sys.stderr, sentence=tokens_list)
        #print(tree.pformat(margin=5, indent=5), file=phrasetrees)
        #print(tree.pformat(margin=5, indent=5))

        if args.phrasesfile != None and not TRUNCATED:
            gold_tree = brackets2tree(gold_phrasetrees[sentence_index],
                    tokens_list)
            gold_tree.pretty_print(sentence=tokens_list, stream=sys.stderr)
        
            if args.reverse:
               count_phrases, count_good = eval_phrase_tree(tree, gold_tree,
                       tokens_list)
            else:
               count_phrases, count_good = eval_phrase_tree(gold_tree, tree,
                       tokens_list)
            if count_phrases > 0:
                score = count_good/count_phrases
                print(count_good, '/', count_phrases, '=', score, file=sys.stderr)
                total_count_sentences += 1
                total_count_phrases += count_phrases
                total_count_good += count_good
                total_sum_scores += score

        # TODO how to eval truncated sentences?
        if args.conllu != None and not TRUNCATED:
            conllu_tree = conllu[sentence_index]
            # build phrasified dep tree
            pdtree = [Tree(tokens_list[i], [i]) for i in range(tokens_count)]
            # mapping child to head
            heads = dict()
            # a queue of unattached nodes (wordpiece prefixes)
            orphans = list()
            root = None
            # e.g. "towel" = "to@@" "wel"
            for child in range(tokens_count):
                if child in conllu_tree:
                    # full word or end of a word: "wel"
                    head = conllu_tree[child]
                    heads[child] = head
                    if head == -1:
                        root = child
                    else:
                        pdtree[head].append(pdtree[child])
                    for orphan in orphans:
                        heads[orphan] = child
                        pdtree[child].append(orphan)
                    orphans = list()
                else:
                    # wordpiece prefix of a word: "to@@"
                    orphans.append(child)

            assert(len(orphans) == 0), "tokens_count=" + str(tokens_count) +  " orphans=" + str(orphans)

            pdtree[root].pretty_print(sentence=tokens_list, stream=sys.stderr)

            # eval phrase tree
            count_phrases = 0
            count_good = 0
            queue = deque()

            if args.reverse:
                # all gold spans
                gold_spans = list()
                queue.append(tree)
                while queue:
                    phrase = queue.popleft()
                    span = phrase.leaves()
                    start = min(span)
                    end = max(span)
                    gold_spans.append((start, end))
                    for subphrase in phrase:
                        if type(subphrase) != int:
                            queue.append(subphrase)
                
                queue.append(pdtree[root])
                while queue:
                    count_phrases += 1
                    phrase = queue.popleft()
                    good = True
                    span = phrase.leaves()
                    start = min(span)
                    end = max(span)

                    for gold_span in gold_spans:
                        gold_start = gold_span[0]
                        gold_end = gold_span[1]
                        if start < gold_end and gold_start < end:
                            # they overlap
                            if start < gold_start and end < gold_end:
                                good = False
                            if start > gold_start and end > gold_end:
                                good = False


                    if good:
                        count_good += 1

                    # recurse
                    for subphrase in phrase:
                        if type(subphrase) != int:
                            queue.append(subphrase)

            else:
    
                queue.append(tree)
                while queue:
                    count_phrases += 1
                    phrase = queue.popleft()
                    good = True
                    span = phrase.leaves()
                    start = min(span)
                    end = max(span)
                    external_root = None
                    external_root_children = 0
                    for child in range(start, end+1):
                        head = heads[child]
                        if head < start or head > end:
                            # dep head of this child is outside this phrase
                            # the phrase can only have one external root
                            if external_root == None:
                                external_root = head
                                external_root_children = 1
                            else:
                                if external_root == head:
                                    external_root_children += 1
                                else:
                                    good = False
                                    break
    
                    for child in range(start, end+1):
                        head = heads[child]
                        require_full_subtree = external_root_children > 1 or (head >= start and head <= end)
                        if require_full_subtree:
                            # dep head of this child is inside this phrase,
                            # or it may be an external head which has multiple children,
                            # thus the whole dep subtree of this child must be
                            # inside this phrase
                            chspan = pdtree[child].leaves()
                            chstart = min(chspan)
                            chend = max(chspan)
                            if chstart < start or chend > end:
                                good = False
                                break
    
                    print(start, tokens_list[start], '...', end, tokens_list[end],
                            ':', good, file=sys.stderr)

                    if good:
                        count_good += 1

                    # recurse
                    for subphrase in phrase:
                        if type(subphrase) != int:
                            queue.append(subphrase)

            score = count_good/count_phrases
            print(count_good, '/', count_phrases, '=', score, file=sys.stderr)
            total_count_sentences += 1
            total_count_phrases += count_phrases
            total_count_good += count_good
            total_sum_scores += score

    
    # draw heatmaps
    if args.visualizations != None:
        for layer in range(layers_count):
            #write_heatmap(tokens_list, sentence_index, vis, layer, 0)
            #write_heatmap(tokens_list, sentence_index, vis, layer, 1)
            for head in range(heads_count):
                write_heatmap(tokens_list, sentence_index, vis, layer, 0, head)
                #write_heatmap(tokens_list, sentence_index, vis, layer, 1, head)

if total_count_sentences > 0:
    macroavg = total_sum_scores / total_count_sentences
    avg = total_count_good / total_count_phrases
    #print('MacroAvg over sentences:', macroavg)
    print(avg)
    #print('Avg over phrases:', total_count_good, '/', total_count_phrases, avg)

if args.colmax:
    output = dict()
    for w in colmaxes_all:
        ratio, count = colmaxes_all[w]
        if count > 3:
            output[w] = ratio / count
    # TODO sort according to ratio, print out
    print("\n\nFINAL", file=colmaxfile)
    for w in sorted(output, key=output.get):
        print("{:4.1f} {}".format(output[w], w), file=colmaxfile)
    colmaxfile.close()

if args.balustradeness:
    for layer in range(layers_count):
        for head in range(heads_count):
            #b = -math.log(balustradeness[layer][head] / sentences_count)
            b = balustradeness[layer][head] / len(args.sentences)
            print('balustradeness of layer', layer, 'head', head, 'is', b)

if deptrees:
    deptrees.close()
if oritrees:
    oritrees.close()

