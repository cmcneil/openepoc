#include <fftw3.h>
/* Code which uses fftw3 library, to be wrapped by Cython NOT FINISHED*/
float *transform(float *vec, int length)
{
	fftwf_complex in*, out*;
	fftwf_plan p;
	
	in = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * length);
	out = (fftwf_complex*) fftwf_malloc(sizeof(fftwf_complex) * length);
	
	p = fftwf_plan_dft_1d(N, in, out, FFTW_FORWARD, FFTW_MEASURE);
	
	
	
}
