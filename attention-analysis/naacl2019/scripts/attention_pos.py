# tom lim
# my approach:
#   - eos token is omitted (attention avaraged for the rest of tokens)
#   - subtoken attentions are averaged
#   - long sentences skipped (TODO: include them)

import argparse
import numpy as np
import matplotlib
from matplotlib import pyplot as plt

from tools import dependency, sentence_attentions
from tools.dependency_converter import DependencyConverter


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


def plot_matrix(matrix):

    fig, ax1 = plt.subplots(figsize=(9,9), ncols=1)
    im = ax1.imshow(matrix,cmap='Blues')
    fig.colorbar(im)
    plt.show()


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--attentions", required=True, help="NPZ file with attentions")
    ap.add_argument("-t", "--tokens", required=True, help="Labels (tokens) separated by spaces")

    ap.add_argument("-p", "--pos", help="Output pos accuracy into this file")
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

    args = ap.parse_args()

    attentions_loaded = np.load(args.attentions)
    sentences_count = len(attentions_loaded.files)
    layers_count = attentions_loaded['arr_0'].shape[0]
    heads_count = attentions_loaded['arr_0'].shape[1]

    with open(args.tokens) as tokens_file:
        tokens_loaded = [l.split() for l in tokens_file]

    # in dependency_rels for each sentece there is a lists of tuples (token, token's head)
    # in dependency_rels_rev tuples are reversed.
    dependency_rels_labeled = dependency.read_conllu_labeled(args.conllu)

    pos = {posl: np.zeros((sentences_count, layers_count, heads_count))
           for posl in dependency.pos_labels}
    pos['root'] = np.zeros((sentences_count, layers_count, heads_count))

    grouped_tokens, _ = dependency.group_wordpieces(tokens_loaded, args.conllu)

    attention_gen = sentence_attentions.generate_matrices(attentions_loaded, grouped_tokens, args.eos, args.no_softmax,
                                                          args.maxlen, args.sentences)
    sentences_considered = []
    for vis, idx in attention_gen:
        sentences_considered.append(idx)
        sent_relations = DependencyConverter(dependency_rels_labeled[idx]).convert(return_root=True)
        
        for layer in range(layers_count):
            for head in range(heads_count):
                deps = vis[layer][head]
                deps = deps.mean(axis=0)
                for token_id, _, rell, posl in sent_relations:
                    pos[posl][idx, layer, head] += deps[token_id]
                    if rell == 'root':
                        pos['root'][idx, layer, head] += deps[token_id]


    for k in pos.keys():
        pos[k] = pos[k][sentences_considered, :, :]
            
        pos[k] = np.mean(pos[k], axis=0)
        pos_filename = f'{args.pos}-{k}.{args.format}'

        heatmap(pos[k], f"Attetention concentration {k}", "heads", "layers", np.arange(heads_count), np.arange(layers_count),
                cmap='summer', color='seagreen', vmax=1.0)

        plt.savefig(pos_filename, dpi=200, format=args.format)
        plt.close()
