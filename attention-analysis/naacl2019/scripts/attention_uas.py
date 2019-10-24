# tom lim
# my approach:
#   - eos token is omitted (attention avaraged for the rest of tokens)
#   - subtoken attentions are averaged
#   - long sentences skipped (TODO: include them)

import argparse
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import sys

from collections import defaultdict

aggregate_args = ('all', 'clausal', 'modifier', 'aux', 'compound', 'conjunct', 'object',
                  'subject', 'determiner', 'other')

dependency_relations = {'acl': 'clausal',
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


def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels, cmap='bone', color='lightblue', vmax=0.5):
    '''
    Copied form:
    https://stackoverflow.com/questions/20574257/constructing-a-co-occurrence-matrix-in-python-pandas
    '''
    # Plot it out
    fig, (ax, ax2) = plt.subplots(1,2,figsize=(16,6), gridspec_kw={'width_ratios': [3, 1]})

    ax.set_xticklabels(xticklabels, minor=False)
    ax.set_yticklabels(yticklabels, minor=False)

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(AUC.shape[1]))
    ax.set_yticks(np.arange(AUC.shape[0]))

    im = ax.imshow(AUC,cmap=cmap, vmin=0, vmax=vmax)
    valfmt = matplotlib.ticker.StrMethodFormatter("{x:.2f}")
    for i in range(AUC.shape[0]):
        for j in range(AUC.shape[1]):
            text = ax.text(j, i, valfmt(AUC[i, j]), ha="center", va="center", color="black")
    fig.colorbar(im, ax=ax, orientation='horizontal')
    ax2.barh(np.arange(AUC.shape[0]),np.mean(AUC,axis=1), color=color)
    #ax2.set_xticks(np.arange(AUC.shape[1]))
    # set title and x/y labels
    fig.suptitle(title)
    
    ax.set_xlabel(xlabel)
    ax2.set_ylabel(ylabel)
    ax.set_ylabel(ylabel)
    ax.invert_yaxis()
    
    ax.set_title('per head')
    ax2.set_title('per layer') #just average


def save_plots(depal_matrix, file_name,file_format, title):
    std_depal = np.std(depal_matrix, axis=0)

    std_filename = file_name + '-std.' + file_format

    heatmap(std_depal, f"DepAl {title} std", "heads", "layers", np.arange(heads_count), np.arange(layers_count),
            cmap='pink', color='sandybrown', vmax=0.3)

    plt.savefig(std_filename, dpi=200, format=file_format)
    plt.close()

    av_depal = np.mean(depal_matrix, axis=0)
    av_filename = file_name + '-average.' + file_format
    heatmap(av_depal, f"DepAl {title} average", "heads", "layers", np.arange(heads_count), np.arange(layers_count))

    plt.savefig(av_filename, dpi=200, format=file_format)
    plt.close()


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
        midres_matrix[tok_id,: ] = np.mean(attention_matrix[wp_ids, :], axis=0)

    res_matrix = np.zeros((len(aggregate_wps), len(aggregate_wps)))

    for tok_id, wp_ids in enumerate(aggregate_wps):
        res_matrix[:, tok_id] = np.sum(midres_matrix[:, wp_ids], axis=1)

    words = ' '.join(wordpieces).replace('@@ ', '')
    res_tokens = words.split()

    assert len(res_tokens) == len(aggregate_wps), "Result matrix and token dimesnions don't match"
    return res_matrix


def add_dependency_relation(drs, head_id, dep_id, label, directional):
    if head_id != 0:
        label = label.split(':')[0] # to cope with nsubj:pass for instance
        if label in dependency_relations:
            label = dependency_relations[label]
        else:
            label = 'other'
        if directional:
            drs['all-p2d'].append((head_id - 1, dep_id - 1))
            drs['all-d2p'].append((dep_id - 1, head_id - 1))
            drs[label + '-p2d'].append((head_id-1, dep_id-1))
            drs[label + '-d2p'].append((dep_id-1, head_id-1))
        
        else:
            drs['all'].append((head_id - 1, dep_id - 1))
            drs['all'].append((dep_id - 1, head_id - 1))
            drs[label].append((head_id-1, dep_id-1))
            drs[label].append((dep_id-1, head_id-1))


def read_conllu(conllu_file, directional=False):
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
                        add_dependency_relation(sentence_rel, int(fields[CONLLU_HEAD]),int(fields[CONLLU_ID]), fields[CONLLU_LABEL], directional)

    return relations


def plot_matrix(matrix):

    fig, ax1 = plt.subplots(figsize=(9,9), ncols=1)
    im = ax1.imshow(matrix,cmap='Blues')
    fig.colorbar(im)
    plt.show()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--attentions", required=True, help="NPZ file with attentions")
    ap.add_argument("-t", "--tokens", required=True, help="Labels (tokens) separated by spaces")

    ap.add_argument("-d", "--depal", help="Output deep alignment measuere into this file")
    ap.add_argument("-c", "--conllu", help="Eval against the given conllu faile")

    ap.add_argument("-f", "--format", default="png",
                    help="Output visualisation as this format (pdf, png, maybe other options)")
    ap.add_argument("-F", "--fontsize", default=8, type=int,
                    help="Fontsize for heatmap; 8 is good for png. 10 is good for PDF it seems")

    ap.add_argument("-s", "--sentences", nargs='*', type=int, default=None,
                    help="Only use the specified sentences; 0-based")
    ap.add_argument("-m", "--maxlen", type=int, default=1000,
                    help="Skip sentences longer than this many words. A word split into several wordpieces is counted as one word. EOS is not counted.")

    ap.add_argument("-e", "--eos", action="store_true",
                    help="Attentions contain EOS")
    
    ap.add_argument("-n", "--no-softmax", action="store_true",
                    help="Whether not to use softmax for attention matrices, use with bert metrices")
    
    ap.add_argument("-b", "--baseline", action="store_true",
                    help="whether to calculate syntax retrival accuracy to compare with baselines ")

    args = ap.parse_args()

    attentions_loaded = np.load(args.attentions)
    sentences_count = len(attentions_loaded.files)
    layers_count = attentions_loaded['arr_0'].shape[0]
    heads_count = attentions_loaded['arr_0'].shape[1]

    with open(args.tokens) as tokens_file:
        tokens_loaded = [l.split() for l in tokens_file]

    # in dependency_rels for each sentece there is a lists of tuples (token, token's head)
    # in dependency_rels_rev tuples are reversed.
    dependency_rels = read_conllu(args.conllu, directional=args.baseline)
    
    if args.baseline:
        dependency_relations.update({ k + '-d2p': v + '-d2p' for k, v in dependency_relations.items()})
        dependency_relations.update({k + '-p2d': v + '-p2d' for k, v in dependency_relations.items()})
        aggregate_args = tuple(ar + '-d2p' for ar in aggregate_args) + tuple(ar + '-p2d' for ar in aggregate_args)
    depals = {aggr: np.zeros((sentences_count, layers_count, heads_count))
              for aggr in aggregate_args}
    
    depals_norm = {aggr: np.zeros((sentences_count, layers_count, heads_count))
              for aggr in aggregate_args}

    for sentence_index in range(sentences_count):
        if args.sentences and sentence_index not in args.sentences:
            continue

        sentence_id = 'arr_' + str(sentence_index)
        tokens_count = attentions_loaded[sentence_id].shape[2]
        if args.eos:
            tokens_count -= 1
        tokens_list = tokens_loaded[sentence_index]

        # check maxlen
        words = ' '.join(tokens_list).replace('@@ ', '')

        words_list = words.split()
        if len(words_list) <= args.maxlen:
            print('Processing sentence', sentence_index, file=sys.stderr)
        else:
            print('Too long sentence, skipped', sentence_index, file=sys.stderr)
            continue

        # NOTE sentences truncated to 64 tokens
        # assert len(tokens_list) == tokens_count, "Bad no of tokens in sent " + str(sentence_index)
        assert len(tokens_list) >= tokens_count, "Bad no of tokens in sent " + str(sentence_index)
        if len(tokens_list) > tokens_count:
            print('Too long sentence, skipped', sentence_index, file=sys.stderr)
            continue

        words_count = len(words_list)

        # for visualisation -- vis[layer][aggreg][head]
        vis = list()

        for layer in range(layers_count):
            layer_deps = list()  # for vis
            layer_matrix = np.zeros((words_count, words_count))
            for head in range(heads_count):
                matrix = attentions_loaded[sentence_id][layer][head]
                if args.eos:
                    matrix = matrix[:-1, :-1]
                # the max trick -- for each row subtract its max
                # from all of its components to get the values into (-inf, 0]
                if not args.no_softmax:
                    matrix = matrix - np.max(matrix, axis=1, keepdims=True)
                    # softmax
                    exp_matrix = np.exp(matrix)
                    deps = exp_matrix/ np.sum(exp_matrix, axis=1, keepdims=True)
                else:
                    deps = matrix / np.sum(matrix, axis=1, keepdims=True)
                deps = aggregate_subtoken_matrix(deps, tokens_list)
                if args.baseline:
                    deps = (deps == deps.max(axis=1)[:,None]).astype(int)
                #layer_deps.append(deps)
                #layer_matrix = layer_matrix + deps

                for k in depals.keys():
                    if len(dependency_rels[sentence_index][k]) == 0:
                        depals[k][sentence_index, layer, head] = 0
                        depals_norm[k][sentence_index, layer, head] = 0
                    else:
                        depals[k][sentence_index, layer, head] \
                                = np.sum(deps[tuple(zip(*dependency_rels[sentence_index][k]))])/np.sum(deps)
                        depals_norm[k][sentence_index, layer, head] = \
                            depals[k][sentence_index, layer, head] * len(deps) / len(dependency_rels[sentence_index][k])

    if args.sentences:
        for k in depals.keys():
            depals[k] = depals[k][args.sentences, :, :]
            depals_norm[k] = depals_norm[k][args.sentences, :, :]

    for k in depals.keys():
        # save_plots(depals[k], args.depal + f'-{k}', args.format, k)
        save_plots(depals_norm[k], args.depal + f'-normed-{k}', args.format, 'normed ' + k)

