#!/usr/bin/python

# This is a module for recording, serializing, and deserializing emotive
# data. It is used to collect datasets.

# TODO: Add options for labeling data using keystrokes.

from emotiv import Emotiv
import time
import gevent
import cPickle as pickle


def record(length, label=""):
    '''Records for length seconds, saving all of the raw data into a pickle
        file.'''
    emotiv = Emotiv(displayOutput=False, research_headset=False)

    print "Beginning Recording..."
    t0 = int(time.time())
    filename = "data/"+str(length)+"sdump"+str(t0)+ "-" + label + ".pkl"
    packet_list = []
    gevent.spawn(emotiv.setup)
    gevent.sleep(1)
    while (time.time() - t0) < length:
        try:
            packet = emotiv.dequeue()
            packet_list.append((packet, label))
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
    '''Loads data from pickle file into a list of objects and returns it.'''
    f = open(filename, "rb")
    lst = pickle.load(f)
    f.close()
    return lst

