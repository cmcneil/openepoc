"""This file will actually perform the machine learning."""

import numpy as np
import emotiv
import dsp
import data
import re

class Classifier:

    def __init__(filelist):
        self.neutral = []
        self.labelled = {}
        for name in filelist:
            label = re.match('\w+-(\w+)\.pkl', name).group(1)
            if label == 'neutral':
                # Load all the data into memory
                neutral.append(emodata.load(name))
            else:
                if name in labelled:
                    labelled[name] = [emodata.load(name)]
                else:
                    labelled[name].append(emodata.load(name))

        emodsp
        
