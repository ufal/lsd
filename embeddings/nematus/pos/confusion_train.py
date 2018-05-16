#!/usr/bin/env python3
# coding: utf-8

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn import svm
from sklearn import linear_model
from sklearn.neural_network import MLPClassifier
from ast import literal_eval as make_tuple
from sklearn.metrics import confusion_matrix
import itertools

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import argparse

parser = argparse.ArgumentParser(description='Train an MLP POS tagger.')
parser.add_argument('--smer')
parser.add_argument('--train', action='store_true')
parser.add_argument('--hls', default='(100,)')
args = parser.parse_args()

smer = args.smer

print(smer)

pos_dict = dict()
with open('../embeddings/pos') as poss:
    for line in poss:
        pos_dict[line.split()[0]] = line.split()[1]

vecs = []
pos = []
with open('../embeddings/' + smer + '/vec_cs_1') as vec_file:
    for line in vec_file:
        wrds = line.split()
        if not pos_dict[wrds[0]] == "NONE":
            vecs.append([float(x) for x in wrds[1:]])
            pos.append(pos_dict[wrds[0]])

vecs = np.array(vecs)
nums = dict((b,a) for (a,b) in enumerate(sorted(list(set(pos)))))
pos_n = np.array([nums[x] for x in pos])

class_names = sorted(list(set(pos)))

print("len(pos):", len(pos))

X_train, X_test, y_train, y_test = train_test_split(
    vecs, pos_n, test_size=0.4, random_state=0)

#hls=(100, 100, 100)
#hls='svm'
#hls='logreg'
hls = args.hls

print(hls)

if hls == 'svm':
    clf = svm.SVC(kernel='linear', C=1)
elif hls == 'logreg':
    clf = linear_model.LogisticRegression()
else:
    hls = make_tuple(hls)
    clf = MLPClassifier(solver='adam', max_iter=500, hidden_layer_sizes=hls)
clf = clf.fit(X_train, y_train)

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

# Compute confusion matrix
if args.train:
    y_pred = clf.predict(X_train)
    cnf_matrix = confusion_matrix(y_train, y_pred)
    train_str='_train'
else:
    y_pred = clf.predict(X_test)
    cnf_matrix = confusion_matrix(y_test, y_pred)
    train_str=''

np.set_printoptions(precision=2)

# Plot non-normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names,
                      title='Confusion matrix, without normalization')
plt.savefig('conf' + train_str + '_unnorm_' + smer + '_' + str(hls) + '.png')

# Plot normalized confusion matrix
plt.figure()
plot_confusion_matrix(cnf_matrix, classes=class_names, normalize=True,
                      title='Normalized confusion matrix')

plt.savefig('conf' + train_str + '_' + smer + '_' + str(hls) + '.png')
