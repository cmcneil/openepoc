"""This file contains methods for loading and parsing information into the
format to be used for learning. Currently, it ~4second bins, and takes the
fourier transform, looking at lower frequency components."""

import emodata
import numpy as np
cimport numpy as np
np.import_array()
##cimport cython
##from libc.stdlib import malloc, free

cdef extern from "stdlib.h":
    void free(void* ptr)
    void* malloc(size_t size)

##a = malloc(10)
##free(a)

cdef extern from "fftw3.h":
    struct fftwf_complex:
        pass

#cdef extern "math.h"

cdef extern from "fourier.h":
    fftwf_complex** transform(float** in_arr, int length)

##def test():
##    cdef float** thing = malloc(8)
##    free(thing)
    
cdef float** npy2c_float2d(np.ndarray[float, ndim=2] a):
    cdef float** a_c = <float**>malloc(a.shape[0] * sizeof(float*))
    for k in range(a.shape[0]):
        a_c[k] = &a[k, 0]
    return a_c

cpdef fourier(data):
    '''Takes in data, fourier transforms all of it.'''
    cdef float** array
    thing = np.zeros([14, 31])
    array = npy2c_float2d(thing)
    ans = transform(array, 31)
    
