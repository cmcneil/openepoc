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
        self.labelled_red = {}
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

    def get_featurevec(self, data):
            '''Takes in data in the form of an array of EmoPackets, and outputs
                a list of feature vectors.'''
            # CHECK THIS: 
            num_bins = (len(data)/int(dsp.SAMPLE_RATE*dsp.STAGGER) -
                        int(dsp.BIN_SIZE / dsp.STAGGER) + 1)
            size = int(dsp.BIN_SIZE*dsp.SAMPLE_RATE)
            starts = int(dsp.SAMPLE_RATE*dsp.STAGGER)
            points = []
            for i in range(num_bins):
                points.append(dsp.get_features(data[i*starts:i*starts+size]))
            return points
        
    def add_data(self, raw, label):
        '''Allows the addition of new data. Will retrain upon addition.
            Expects a list of EmoPackets.'''
        if label == 'neutral':
            self.neutral.extend(self.get_featurevec(raw))
        else:
            if label in self.labelled:
                self.labelled[label].extend(self.get_featurevec(raw))
            else:
                self.labelled[label] = self.get_featurevec(raw)

##        self.reduce_dim()
##        self.train()

    def extract_features(self):
        '''Does feature extraction for all of the datasets.'''
        self.neutral = []
        for sess in self.raw_neutral:
            self.neutral.extend(self.get_featurevec(sess))
        for key in self.raw_labelled:
            self.labelled[key] = []
            for sess in self.raw_labelled[key]:
                self.labelled[key].extend(self.get_featurevec(sess))

    def reduce_dim(self):
        '''Reduces the dimension of the extracted feature vectors.'''
        NDIM = 5
        X = np.array(self.neutral)
        pca = RandomizedPCA(n_components=NDIM).fit(X)
        print pca.explained_variance_ratio_
        self.neutral_red = pca.transform(X)
        for label in self.labelled:
            X = np.array(self.labelled[label])
            self.labelled_red[label] = pca.transform(X)

    def train(self):
        '''Trains the classifier.'''
        lab = self.labelled_red.keys()[0]

        X_train = np.concatenate((self.neutral_red,
                                  self.labelled_red[lab]), axis=0)
        y_train = np.array([0]*len(self.neutral_red) +
                           [1]*len(self.labelled_red[lab]))

        self.svm = SVC(kernel='poly')
        self.svm.fit(X_train, y_train)

    def classify(self, data):
        ''''Classify a point. Expects a bunch of packets.'''
        X = self.get_featurevec(data)[0]
        return self.svm.predict(X)

    def test_SVM(self):
        '''Splits the sets into training sets and test sets.'''
        perc = 8 # Will use 1/perc of the data for the test set.
        lab = self.labelled_red.keys()[0]
        test_neutral = self.neutral_red_red[len(self.neutral_red)-len(self.neutral_red)/perc:]
        test_lab = self.labelled_red[lab][len(self.labelled_red[lab])-\
                                      len(self.labelled_red[lab])/perc:]

        X_test = np.concatenate((test_neutral, test_lab), axis=0)
        y_test = np.array([0]*len(test_neutral) + [1]*len(test_lab))

        neutral_train = self.neutral_red[:len(self.neutral_red)-len(self.neutral_red)/perc]
        label_train = self.labelled_red[lab][:len(self.labelled_red[lab])-\
                                      len(self.labelled_red[lab])/perc]

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

        
