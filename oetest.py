'''An extremely simplistic test. Really only ensures it doesn't throw errors.'''
import openepoc as oe
classif = oe.learn.Classifier(['data/10sdump1360740702-push.pkl', 'data/30sdump1360740620-neutral.pkl'])
classif.extract_features()
red_dim = classif.reduce_dim()
