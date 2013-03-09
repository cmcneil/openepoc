'''An extremely simplistic test. Really only ensures it doesn't throw errors.
Also tests classification.'''
import openepoc.api as emo
import gevent

name = 'Test'
profile = emo.Profile(name)

print "Training Neutral State"
emo.train_command(profile, 9)
print "Train Push Command in 3."
c = 3
while c > 0:
    print str(c) + '...'
    c -= 1
    gevent.sleep(1)
emo.train_command(profile, 9, label='push')

commands = emo.get_command_queue(profile)

while True:
    cmd = commands.get()
    print 'neutral: ' + str(cmd[0, 0]) + ', push: ' + str(cmd[0, 1])
