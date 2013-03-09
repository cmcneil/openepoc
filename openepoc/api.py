#!/usr/bin/env python

from emotiv import Emotiv
from learn import Profile
import time
import gevent
import dsp
import re
import cPickle as pickle

emotiv = Emotiv(displayOutput=False, research_headset=False)
gevent.spawn(emotiv.setup)
gevent.sleep(0)

def load_profile(filename):
    '''Returns a Profile loaded from that filename.'''
    f = open(filename, "rb")
    profile = pickle.load(f)
    f.close()
    return profile

def test_commands(profile, files):
    '''Given a list of files, extracts the data, and tests the outcome.'''
    test_data = []
    for f in files:
        f = open(filename, "rb")
        packet_list = pickle.load(f)
        label = re.match('[\w/]+-(\w+)\.pkl', filename).group(1)
        test_data.append((packet_list, label))
    profile.test_accuracy(self, test_data)
        

def train_command(profile, t=None, filename=None, label='neutral'):
    '''Trains the state of profile for t seconds.'''
    if filename != None:
        f = open(filename, "rb")
        packet_list = pickle.load(f)
        label = re.match('[\w/]+-(\w+)\.pkl', filename).group(1)
    else:
        packet_list = []
        emotiv.clear()
        gevent.sleep(0)
        t0 = time.time()
        while (time.time() - t0) < t:
            packet = emotiv.dequeue()
            packet_list.append(packet)
    profile.add_data(packet_list, label)
    profile.reduce_dim()
    profile.train() 
    return True

def get_command_queue(profile):
    '''Returns a gevent Queue which will be filled with the appropriate
        commands. Spawns a Greenlet which fills the Queue.'''
    def listen(profile, q):
        '''Worker for the greenlet Thread.'''
        packet_list = []
        temp_list = []
        emotiv.clear()
        gevent.sleep(0)
        while len(packet_list) < dsp.BIN_SIZE * dsp.SAMPLE_RATE:
            packet = emotiv.dequeue()
            packet_list.append(packet)
            
        while True:
            packet = emotiv.dequeue()
            temp_list.append(packet)
            
            if len(temp_list) > dsp.STAGGER * dsp.SAMPLE_RATE:
                packet_list.extend(temp_list)
                packet_list = packet_list[len(temp_list):]
                ans = profile.classify(packet_list)
                q.put_nowait(ans)
                temp_list = []
                gevent.sleep(0)
                
    q = gevent.queue.Queue()
    gevent.spawn(listen, profile, q)
    return q

    

