# tom lim
# my approach:
#   - eos token is omitted (attention avaraged for the rest of tokens)
#   - subtoken attentions are averaged

import argparse
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
import sys


def heatmap(AUC, title, xlabel, ylabel, xticklabels, yticklabels):
    '''
    Copied form:
    https://stackoverflow.com/questions/20574257/constructing-a-co-occurrence-matrix-in-python-pandas
    '''
    # Plot it out
    fig, ax = plt.subplots(figsize=(16,6))


    ax.set_xticklabels(xticklabels, minor=False)
    ax.set_yticklabels(yticklabels, minor=False)

    # put the major ticks at the middle of each cell
    ax.set_xticks(np.arange(AUC.shape[1]))
    ax.set_yticks(np.arange(AUC.shape[0]))

    im = ax.imshow(AUC,cmap='Blues')
    fig.colorbar(im)
    # set title and x/y labels
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)



def aggregate_subtoken_matrix(attention_matrix, wordpieces):
    aggregate_wps = []
    wp_ids = []
    for wp_id, wp in enumerate(wordpieces):
        wp_ids.append(wp_id)
        if not wp.endswith('@@'):
            aggregate_wps.append(wp_ids)
            wp_ids = []

    midres_matrix = np.zeros((len(wordpieces), len(aggregate_wps)))

    for tok_id, wp_ids in enumerate(aggregate_wps):
        midres_matrix[tok_id,: ] = np.mean(attention_matrix[wp_ids, :], axis=0)

    res_matrix = np.zeros((len(aggregate_wps), len(aggregate_wps)))

    for tok_id, wp_ids in enumerate(aggregate_wps):
        res_matrix[:, tok_id] = np.sum(midres_matrix[:, wp_ids], axis=1)

    words = ' '.join(wordpieces).replace('@@ ', '')
    res_tokens = words.split()

    assert len(res_tokens) == len(aggregate_wps), "Result matrix and token dimesnions don't match"
    return res_matrix


def read_conllu(conllu_file):
    CONLLU_ID = 0
    CONLLU_HEAD = 6
    relations = []
    reverse_relations = []
    sentence_rel = []
    sentence_rev_rel = []
    with open(args.conllu) as conllu_file:
        sentid = 0
        for line in conllu_file:
            if line == '\n':
                relations.append(sentence_rel)
                sentence_rel = []
                
                reverse_relations.append(sentence_rel)
                sentence_rev_rel = []
                sentid += 1
            elif line.startswith('#'):
                continue
            else:
                fields = line.strip().split('\t')
                if fields[CONLLU_ID].isdigit():
                    if int(fields[CONLLU_HEAD]) != 0:
                        sentence_rel.append((int(fields[CONLLU_ID])-1, int(fields[CONLLU_HEAD])-1))
                        sentence_rev_rel.append((int(fields[CONLLU_HEAD])-1,int(fields[CONLLU_ID])-1))

    return relations, reverse_relations


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

    ap.add_argument("-s", "--sentences", nargs='+', type=int, default=[4, 5, 6],
                    help="Only use the specified sentences; 0-based")
    ap.add_argument("-m", "--maxlen", type=int, default=1000,
                    help="Skip sentences longer than this many words. A word split into several wordpieces is counted as one word. EOS is not counted.")

    ap.add_argument("-e", "--eos", action="store_true",
                    help="Attentions contain EOS")

    args = ap.parse_args()

    attentions_loaded = np.load(args.attentions)
    sentences_count = len(attentions_loaded.files)
    layers_count = attentions_loaded['arr_0'].shape[0]
    heads_count = attentions_loaded['arr_0'].shape[1]

    with open(args.tokens) as tokens_file:
        tokens_loaded = [l.split() for l in tokens_file]

    # in dependency_rels for each sentece there is a lists of tuples (token, token's head)
    # in dependency_rels_rev tuples are reversed.
    dependency_rels, dependency_rels_rev = read_conllu(args.conllu)

    depal = np.zeros((sentences_count, layers_count, heads_count))

    for sentence_index in range(sentences_count):
        if args.sentences and sentence_index in args.sentences:
            pass
        else:
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
                matrix = np.transpose(np.transpose(matrix) - np.max(matrix, axis=1))
                # softmax
                exp_matrix = np.exp(matrix)
                deps = np.transpose(np.transpose(exp_matrix) / np.sum(exp_matrix, axis=1))
                deps = aggregate_subtoken_matrix(deps, tokens_list)
                #layer_deps.append(deps)
                #layer_matrix = layer_matrix + deps

                depal[sentence_index, layer, head] = np.sum(deps[tuple(zip(*dependency_rels[sentence_index]))])/np.sum(deps)

    if args.sentences:
        depal = depal[args.sentences, :, :]

    std_depal = np.std(depal, axis=0)

    std_filename = args.depal + '-std.' + args.format

    heatmap(std_depal, "DepAl std", "heads", "layers", np.arange(heads_count), np.arange(layers_count))

    plt.savefig(std_filename, dpi=200, format=args.format)
    plt.close()

    av_depal = np.mean(depal, axis=0)
    av_filename = args.depal + '-average.' + args.format
    heatmap(av_depal, "DepAl average", "heads", "layers", np.arange(heads_count), np.arange(layers_count))

    plt.savefig(av_filename, dpi=200, format=args.format)
    plt.close()
