#!/usr/bin/env python

from emotiv import Emotiv
import learn
import time
import gevent
import dsp

emotiv = Emotiv(displayOutput=False, research_headset=False)
gevent.sleep(2)
gevent.spawn(emotiv.setup)
gevent.sleep(0.2)

cls = learn.Profile([])
print "Beginning..."

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
    try:
        packet = emotiv.dequeue()
        packet_list.append(packet)
    except gevent.queue.Empty, e:
        print "Queue is empty!"
        pass
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
        try:
            packet = emotiv.dequeue()
            packet_list.append(packet)
        except gevent.queue.Empty, e:
            print "Queue is empty!"
            pass
    profile.add_data(packet_list, label)
    profile.reduce_dim()
    profile.train()
    return True

def get_command_queue(profile):
    q = gevent.Queue()
    gevent.spawn(profile, q)
    return q
    
def listen(profile, q):
    packet_list = []
    temp_list = []
    emotiv.clear()
    gevent.sleep(0)
    while len(packet_list) < dsp.BIN_SIZE * dsp.SAMPLE_RATE:
        try:
            packet = emotiv.dequeue()
            packet_list.append(packet)
        except gevent.queue.Empty, e:
            print "Queue is empty!"
            pass
        
    while True:
        try:
            packet = emotiv.dequeue()
            temp_list.append(packet)
        except gevent.queue.Empty, e:
            print "Queue is empty!"
            pass
        if len(temp_list) > dsp.STAGGER * dsp.SAMPLE_RATE:
            packet_list.extend(temp_list)
            packet_list = packet_list[len(temp_list):]
            ans = profile.classify(packet_list)
            q.put(ans)
            temp_list = []
            gevent.sleep(0)

##print "Training neutral state. Relax."



##while (time.time() - t0) < NTRAIN:
##    try:
##        packet = emotiv.dequeue()
##        packet_list.append(packet)
##    except gevent.queue.Empty, e:
##        print "Queue is empty!"
##        pass
##cls.add_data(packet_list, 'neutral')
##emotiv.close()
##gevent.shutdown()

print "Now concentrate on a push command in 3."
##emotiv = Emotiv(displayOutput=False, research_headset=False)
##gevent.sleep(2)
##gevent.spawn(emotiv.setup)
##gevent.sleep(3)
##emotiv.clear()
##t0 = time.time()
##while (time.time() - t0) < 3:
##    try:
##        packet = emotiv.dequeue()
##    except gevent.queue.Empty, e:
##        print "Queue is empty!"
##        pass
    
##gevent.sleep(0.2)
##print "Recording..."
##t0 = time.time()
##packet_list = []
##while (time.time() - t0) < PTRAIN:
##    try:
##        packet = emotiv.dequeue()
##        packet_list.append(packet)
##    except gevent.queue.Empty, e:
##        print "Queue is empty!"
##        pass
##cls.add_data(packet_list, 'push')
##cls.reduce_dim()
##cls.train()
##
##packet_list = []
##temp_list = []
##emotiv.clear()
##gevent.sleep(0)
##while len(packet_list) < dsp.BIN_SIZE * dsp.SAMPLE_RATE:
##    try:
##        packet = emotiv.dequeue()
##        packet_list.append(packet)
##    except gevent.queue.Empty, e:
##        print "Queue is empty!"
##        pass
##
##print "Queue filled with " +str(len(packet_list))
##
####t0 = time.time()
##while True:
##    try:
##        packet = emotiv.dequeue()
##        temp_list.append(packet)
##    except gevent.queue.Empty, e:
##        print "Queue is empty!"
##        pass
##    if len(temp_list) > dsp.STAGGER * dsp.SAMPLE_RATE:
##        packet_list.extend(temp_list)
##        packet_list = packet_list[len(temp_list):]
##        ans = cls.classify(packet_list)
####        print time.time() - t0
##        print ans
##        temp_list = []


