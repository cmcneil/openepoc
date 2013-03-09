openepoc
========

A few open source ML libraries for emotiv's EPOC. The goal is to create a high level Python API to allow developers to train high level digital controls from EPOC data and use these controls in their applications.  
Depends on <a href="https://github.com/cmcneil/emokit">my fork</a> of qdot's emokit. 

Dependencies
--------------------

* <a href="https://github.com/cmcneil/emokit">My fork</a> of qdot's emokit, and all the dependencies of emokit.
* python and standard libraries.
* python-numpy
* <a href="http://scikit-learn.org/stable/">scikit-learn</a>
* <a href="http://www.gevent.org/">Gevent</a>

Example Use
------------------
I'm attempting to make an API that's very easy to use, and is similar to Emotiv's SDK.(Inferring from control panel, as I have never used their SDK :P)

```python
import openepoc.api as emo
    
# Create a new Profile. This keeps track of training sessions for a particular      
# person. It may be useful to make one every time someone puts on the
# headset, as putting it on differently can change the signal.
profile = emo.Profile("carson")

emo.train_command(profile, 20) # Trains the neutral state for 20s
emo.train_command(profile, 12, label='push') # Trains the push command for 12s

commands = emo.get_command_queue(profile) # returns a gevent Queue which will fill with commands.

while True:
    cmd = commands.get()
    print "Command: " + str(cmd)
```    


