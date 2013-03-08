#!/usr/bin/python

# This is a module for recording, serializing, and deserializing emotive
# data. It is used to collect datasets.

# TODO: Add options for labeling data using keystrokes.

import emotiv
from emotiv import Emotiv
#from emotiv import *
import time
import gevent
import cPickle as pickle


def record(length, label=""):
    '''Records for length seconds, saving all of the raw data into a pickle
        file.'''
    emotiv = Emotiv(displayOutput=False, research_headset=False)

    print "Beginning Recording..."
    t0 = int(time.time())
    filename = str(length)+"sdump"+str(t0)+ "-" + label + ".pkl"
    packet_list = []
    gevent.spawn(emotiv.setup)
    gevent.sleep(1)
    while (time.time() - t0) < length:
        try:
            packet = emotiv.dequeue()
            packet_list.append(packet)
        except gevent.queue.Empty, e:
            print "Queue is empty!"
            pass
    emotiv.close()
    print "Done!"
    print "Writing Data..."
    dumpfile = open(filename, "wb")
    pickle.dump(packet_list, dumpfile, pickle.HIGHEST_PROTOCOL)
    dumpfile.close()
    print "Data Written to " + filename + "!"

def load(filename):
    '''Loads data from pickle file into a list tuples of the form:
        (EmoPacket, label). label is "" if we are doing unsupervised.
        This allows us to interleave labeled and unlabeled packets from
        a single recording session into one file.'''
    f = open(filename, "rb")
    lst = pickle.load(f)
    f.close()
    return lst

