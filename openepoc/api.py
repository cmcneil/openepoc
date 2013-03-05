#!/usr/bin/env python

from emotiv import Emotiv
import learn
import time

FPS = 5
NTRAIN = 30
PTRAIN = 10

emotiv = Emotiv(displayOutput=False, research_headset=False)
cls = learn.Classifier([])
print "Beginning..."

gevent.sleep(2)
gevent.spawn(emotiv.setup)
gevent.sleep(1)
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
emotiv.close()
gevent.shutdown()

print "Now concentrate on a push command in 3."
emotiv = Emotiv(displayOutput=False, research_headset=False)
gevent.sleep(2)
gevent.spawn(emotiv.setup)
gevent.sleep(1)
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
        temp_list.append(packet)
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
        packet_list.append(temp_list)
        temp_list = []
        packet_list = packet_list[len(temp_list):]
        ans = cls.classif(packet_list)
        print ans      


