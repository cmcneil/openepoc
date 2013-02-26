"""This file will actually perform the machine learning."""

import numpy as np
import emotiv
import dsp
import data
import re

from sklearn.decomposition import RandomizedPCA

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
            num_bins = (len(data)/int(dsp.SAMPLE_RATE*dsp.STAGGER) -
                        int(dsp.BIN_SIZE) + 1)
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
        pca = RandomizedPCA(n_components=6)
        X = np.array(self.neutral)
        print X
        print X.shape
        pca.fit(X)
        neutral_new = pca.transform(X)
        return neutral_new
