"""This file contains methods for loading and parsing information into the
format to be used for learning. Currently, it ~4second bins, and takes the
fourier transform, looking at lower frequency components."""

import emodata
import emotiv
import numpy as np
import fftw3f

SAMPLE_RATE = 128.0 # Hz, the rate at which emotiv packets arrive.
NUM_ELECS = 14
BIN_SIZE = 4.0 # Seconds, the size of a given timesample to be used as the unit.
STAGGER = 1.0 # The number of seconds by which we stagger samples.
FREQ_CUTOFF = 13 # The feature vector will only contain the first FREQ_CUTOFF
                 # frequencies, which are spaced based on BIN_SIZE
                 # and SAMPLE_FREQ

freqs = np.fft.fftfreq(int(BIN_SIZE * SAMPLE_RATE), d=1.0/SAMPLE_RATE)

def fastest_fourier(data):
    '''Takes a matrix of the data and fourier transforms all of it.'''
    indata = np.zeros(data.shape, dtype='float')
    outdata = np.zeros(data.shape, dtype='float')
    fft = fftw3f.Plan(indata,outdata, direction='forward', flags=['measure'],
                      realtypes=[])
    fft.execute()

def get_features(packets):
    '''This function will return a feature vector when given a particular
        bin of emotiv data, expected in the form of an array of Packets'''
    if len(bin_data) != int(BIN_SIZE * SAMPLE_RATE):
        raise EmoDSPException
    data = np.array(map(lambda p : p.get_values(),
                        packets), order='F').transpose()
    pows = np.abs(np.fft.fft(data))[:, :FREQ_CUTOFF]
    return pows.flatten()
    
class EmoDSPException(Exception):
    pass
##cdef float** npy2c_float2d(np.ndarray[float, ndim=2] a):
##    cdef float** a_c = <float**>malloc(a.shape[0] * sizeof(float*))
##    for k in range(a.shape[0]):
##        a_c[k] = &a[k, 0]
##    return a_c

