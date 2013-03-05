"""This file will actually perform the machine learning."""

import numpy as np
import emotiv
import dsp
import data
import re

from sklearn.decomposition import RandomizedPCA
from sklearn.svm import SVC
from sklearn.cross_validation import cross_val_score

class Classifier:
    def __init__(self, filelist):
        self.raw_neutral = []
        self.neutral = []
        self.labelled = {}
        self.raw_labelled = {}
        for name in filelist:
            label = re.match('[\w/]+-(\w+)\.pkl', name).group(1)
            if label == 'neutral':
                # Load all the data into memory
                self.raw_neutral.append(data.load(name))
            else:
                if label in self.labelled:
                    self.raw_labelled[label].append(data.load(name))
                else:
                    self.raw_labelled[label] = [data.load(name)]

    def extract_features(self):
        '''Does feature extraction for all of the datasets.'''
        
        def get_featurevec(data):
            # CHECK THIS: 
            num_bins = (len(data)/int(dsp.SAMPLE_RATE*dsp.STAGGER) -
                        int(dsp.BIN_SIZE / dsp.STAGGER) + 1)
            size = int(dsp.BIN_SIZE*dsp.SAMPLE_RATE)
            starts = int(dsp.SAMPLE_RATE*dsp.STAGGER)
            points = []
            for i in range(num_bins):
                points.append(dsp.get_features(data[i*starts:i*starts+size]))
            return points
        
        self.neutral = []
        print "NEUTRAL**********"
        for sess in self.raw_neutral:
            self.neutral.extend(get_featurevec(sess))
        for key in self.raw_labelled:
            print "LABEL:"+str(key)+"************"
            self.labelled[key] = []
            for sess in self.raw_labelled[key]:
                self.labelled[key].extend(get_featurevec(sess))

    def reduce_dim(self):
        '''Reduces the dimension of the extracted feature vectors.'''
        NDIM = 5
        X = np.array(self.neutral)
        pca = RandomizedPCA(n_components=NDIM).fit(X)
        print pca.explained_variance_ratio_
        self.neutral = pca.transform(X)
        for label in self.labelled:
            X = np.array(self.labelled[label])
            self.labelled[label] = pca.transform(X)

    def train(self):
        '''Trains the classifier.'''
        lab = self.labelled.keys()[0]

        X_train = np.concatenate((self.neutral, self.labelled[lab]), axis=0)
        y_train = np.array([0]*len(self.neutral) + [1]*len(self.labelled[lab]))

        self.svm = SVC(kernel='poly')
        self.svm.fit(X_train, y_train)

    def test_SVM(self):
        '''Splits the sets into training sets and test sets.'''
        perc = 8 # Will use 1/perc of the data for the test set.
        lab = self.labelled.keys()[0]
        test_neutral = self.neutral[len(self.neutral)-len(self.neutral)/perc:]
        test_lab = self.labelled[lab][len(self.labelled[lab])-\
                                      len(self.labelled[lab])/perc:]

        X_test = np.concatenate((test_neutral, test_lab), axis=0)
        y_test = np.array([0]*len(test_neutral) + [1]*len(test_lab))

        neutral_train = self.neutral[:len(self.neutral)-len(self.neutral)/perc]
        label_train = self.labelled[lab][:len(self.labelled[lab])-\
                                      len(self.labelled[lab])/perc]

        X_train = np.concatenate((neutral_train, label_train), axis=0)
        y_train = np.array([0]*len(neutral_train) + [1]*len(label_train))
        
##        gammas = [0.00001, 0.001, 0.01, 0.1, 0.2, 0.4, 1.0, 2.5]
##        best_gamma = (0.1, 0.0)
##        for test in gammas:
##            potential = SVC(gamma=test)
##            score = cross_val_score(potential, X_train, y_train, cv=8).mean()
##            potential.fit(X_train, y_train)
##            print "support vectors: " + str(potential.n_support_)
##            if score > best_gamma[1]:
##                best_gamma = (test, score)

##        kernels = ['linear', 'poly', 'sigmoid']
##        for kern in kernels:
##            potential = SVC(kernel=kern)
####            score = cross_val_score(potential, X_train, y_train, cv=8).mean()
##            potential.fit(X_train, y_train)
##            print "support vectors: " + str(potential.n_support_)
##            print "score: " + str(potential.score(X_test, y_test))
        
        svm = SVC(kernel='poly')
        svm.fit(X_train, y_train)
        print "Number of support vectors: " + str(svm.n_support_)
        print svm.score(X_test, y_test).mean()

        
