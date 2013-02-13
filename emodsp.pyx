"""This file contains methods for loading and parsing information into the
format to be used for learning. Currently, it ~4second bins, and takes the
fourier transform, looking at lower frequency components."""

import emodata


cdef extern from "fftw3.h"
cdef extern 
def fourier():
