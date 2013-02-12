#!/usr/bin/python

# This is a module for recording, serializing, and deserializing emotive
# data. It is used to collect datasets.

# TODO: Add options for labeling data using keystrokes.

from emotive import Emotiv
import time
import gevent
import pickle


def record(length):
    '''Records for length seconds, saving all of the raw data into a pickle
        file.'''
    emotiv = Emotiv(displayOutput=False)

    print "Beginning Recording..."
    t0 = time.clock()
    filename = "data/"+str(length)+"sdump"+str(t0)+".pkl"
    packet_list = []
    gevent.spawn(emotiv.setup)
    while (time.clock - t0) < length:
    try:
        packet = emotiv.dequeue()
    except Empty, e:
        pass
    packet_list.append(packet)
    emotiv.close()
    print "Done!"
    print "Writing Data..."
    dumpfile = open(filename, "wb")
    pickle.dump(packet_list, dumpfile, pickle.HIGHEST_PROTOCOL)
    dumpfile.close()
    print "Data Written to " + filename + "!"

def load(filename):
    f = open(filename, "rb")
    lst = pickle.load(f)
    f.close()
    return lst

