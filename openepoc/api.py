#!/usr/bin/env python

from emotiv import Emotiv
import learn
import time
import gevent
import dsp

emotiv = Emotiv(displayOutput=False, research_headset=False)
gevent.spawn(emotiv.setup)
gevent.sleep(0)

def new_profile():
    '''Returns a new Profile.'''
    cls = learn.Profile([])
    return cls

def train_neutral(profile, t):
    '''Trains the neutral state of profile for t seconds.'''
    packet_list = []
    emotiv.clear()
    gevent.sleep(0)
    t0 = time.time()
    while (time.time() - t0) < t:
        packet = emotiv.dequeue()
        packet_list.append(packet)
    profile.add_data(packet_list, 'neutral')
    profile.reduce_dim()
    profile.train() 
    return True

def train_command(profile, label, t):
    '''Trains a profile with a label for t seconds.'''
    t0 = time.time()
    packet_list = []
    emotiv.clear()
    gevent.sleep(0)
    while (time.time() - t0) < t:
        packet = emotiv.dequeue()
        packet_list.append(packet)
    profile.add_data(packet_list, label)
    profile.reduce_dim()
    profile.train()
    return True

def get_command_queue(profile):
    q = gevent.queue.Queue()
    gevent.spawn(listen, profile, q)
    return q
    
def listen(profile, q):
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
