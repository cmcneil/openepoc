#!/usr/bin/env python

from emotiv import Emotiv
import learn
import time
import gevent
import dsp

FPS = 5
NTRAIN = 30
PTRAIN = 20

emotiv = Emotiv(displayOutput=False, research_headset=False)
cls = learn.Classifier([])
print "Beginning..."

gevent.sleep(2)
gevent.spawn(emotiv.setup)
gevent.sleep(0.2)
print "Training neutral state. Relax."

t0 = time.time()
packet_list = []

while (time.time() - t0) < NTRAIN:
    try:
        packet = emotiv.dequeue()
        packet_list.append(packet)
    except gevent.queue.Empty, e:
        print "Queue is empty!"
        pass
cls.add_data(packet_list, 'neutral')
##emotiv.close()
##gevent.shutdown()

print "Now concentrate on a push command in 3."
##emotiv = Emotiv(displayOutput=False, research_headset=False)
##gevent.sleep(2)
##gevent.spawn(emotiv.setup)
gevent.sleep(3)
emotiv.clear()
##t0 = time.time()
##while (time.time() - t0) < 3:
##    try:
##        packet = emotiv.dequeue()
##    except gevent.queue.Empty, e:
##        print "Queue is empty!"
##        pass
    
gevent.sleep(0.2)
print "Recording..."
t0 = time.time()
packet_list = []
while (time.time() - t0) < PTRAIN:
    try:
        packet = emotiv.dequeue()
        packet_list.append(packet)
    except gevent.queue.Empty, e:
        print "Queue is empty!"
        pass
cls.add_data(packet_list, 'push')
cls.reduce_dim()
cls.train()

packet_list = []
temp_list = []
while len(packet_list) < dsp.BIN_SIZE * dsp.SAMPLE_RATE:
    try:
        packet = emotiv.dequeue()
        packet_list.append(packet)
    except gevent.queue.Empty, e:
        print "Queue is empty!"
        pass

print "Queue filled with " +str(len(packet_list))

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
        ans = cls.classify(packet_list)
        print ans
        temp_list = []


