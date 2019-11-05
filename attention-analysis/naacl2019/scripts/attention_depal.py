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

import dependency, sentence_attentions


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

    # save standard deviation if needed
    
    # std_depal = np.std(depal_matrix, axis=0)
    # std_filename = file_name + '-std.' + file_format
    #
    # heatmap(std_depal, f"DepAl {title} std", "heads", "layers", np.arange(heads_count), np.arange(layers_count),
    #         cmap='pink', color='sandybrown', vmax=0.3)
    # plt.savefig(std_filename, dpi=200, format=file_format)
    # plt.close()

    av_depal = np.mean(depal_matrix, axis=0)
    av_filename = file_name + '-average.' + file_format
    heatmap(av_depal, f"DepAl {title} average", "heads", "layers", np.arange(heads_count), np.arange(layers_count))

    plt.savefig(av_filename, dpi=200, format=file_format)
    plt.close()


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
    
    ap.add_argument("-2", "--two-directions", action="store_true",
                    help="whether to consider directionality ")

    args = ap.parse_args()

    attentions_loaded = np.load(args.attentions)
    sentences_count = len(attentions_loaded.files)
    layers_count = attentions_loaded['arr_0'].shape[0]
    heads_count = attentions_loaded['arr_0'].shape[1]

    with open(args.tokens) as tokens_file:
        tokens_loaded = [l.split() for l in tokens_file]

    # in dependency_rels for each sentece there is a lists of tuples (token, token's head)
    # in dependency_rels_rev tuples are reversed.
    dependency_rels = dependency.read_conllu(args.conllu, directional=args.two_directions)

    depals = {aggr: np.zeros((sentences_count, layers_count, heads_count))
              for aggr in dependency.labels}
    
    depals_norm = {aggr: np.zeros((sentences_count, layers_count, heads_count))
                   for aggr in dependency.labels}
    
    grouped_tokens, _ = dependency.group_wordpieces(tokens_loaded, args.conllu)

    attention_gen = sentence_attentions.generate_matrices(attentions_loaded, grouped_tokens, args.eos, args.no_softmax,
                                                            args.maxlen, args.sentences)
    for vis, idx in attention_gen:
        for layer in range(layers_count):
            for head in range(heads_count):
                deps = vis[layer][head]
                for k in depals.keys():
                    if len(dependency_rels[idx][k]) == 0:
                        depals[k][idx, layer, head] = 0
                        depals_norm[k][idx, layer, head] = 0
                    else:
                        depals[k][idx, layer, head] \
                            = np.sum(deps[tuple(zip(*dependency_rels[idx][k]))]) / np.sum(deps)
                        depals_norm[k][idx, layer, head] = \
                            depals[k][idx, layer, head] * len(deps) / len(dependency_rels[idx][k])
                    
    if args.sentences:
        for k in depals.keys():
            depals[k] = depals[k][args.sentences, :, :]
            depals_norm[k] = depals_norm[k][args.sentences, :, :]

    for k in depals.keys():
        # save_plots(depals[k], args.depal + f'-{k}', args.format, k)
        save_plots(depals_norm[k], args.depal + f'-normed-{k}', args.format, 'normed ' + k)

