/*! \file adc.h

	\author Scott Livingston

	\brief Prototypes for ADC application.  Note that this code was
	       written only with the x2274 chip and GoodFET31 in mind;
	       specifically, pin 5 of the (JTAG) header is sampled.
	       Supporting x2618, x1611/12 and other GoodFET boards remains!
	       For timing considerations, see at least Section 20.2.5
	       "Sample and Conversion Timing" (on page 589?) of msp430x2xx
	       family manual.

	\date September 2010
*/

#ifndef ADC_H
#define ADC_H

#include "command.h"
#include "app.h"

#define ADC 0x74

//! Initialize ADC10 module (specific to 2xx chip family).
void init_adc10();

//! Uninit/stop ADC10 module (specific to 2xx chip family).
void uninit_adc10();

//! Return a single, instantaneous sample.
u16 sample_adc10();

//! Fill cmddata string; sampling repeatedly at a fixed rate.
u16 nsamples_adc10( u8 N_count, //! Number samples to obtain (bounded w.r.t. cmddata)
										u8 t_sample, /*! sample-and-hold time; this is
																     written directly to ADC10SHTx
																		 field of ADC10CTL0 register;
																		 possible values are
																		 00   4 ADC10CLK ticks,
																		 01   8 ADC10CLK ticks,
																		 10  16 ADC10CLK ticks,
																		 11  64 ADC10CLK ticks. */
										u8 clock_div ); /*! Value by which to divide SMCLK
																			  (which is assumed to be 16
																			  MHz), then giving
																			  ADC10CLK.
																				Possible values are 1..8
																				Cf. Fig. 20-1 (on page 585?)
																			  of the msp430x2xxx family
																			  manual. */


//! Command codes
#define ADC10_INIT    0x81 //! Initialize ADC10 module (i.e., get ready for sampling).
#define ADC10_UNINIT  0x82 //! Uninitialize (or "stop") ADC10.
#define ADC10_1SAMPLE 0x83 //! Capture a single sample.

/*! Capture a sequence of samples at a constant rate and write result
    till requested number of samples is acquired or cmddata array is
    filled, whichever is smaller. Hence, in the maximum length case,
    (CMDDATALEN-4)/2 10-bit samples are obtained (128 total using
    x2274 chip).

    The command has several possible formats, switched according to
    the length of received command data (from client). See above
    comments about nsamples_adc10 function for meaning of ``t_samlpe''
    and ``clock_div.''
    
    length 0  =>  max sample sequence length, t_sample = 3, clock_div = 8;
           1  =>  user-specified sequence length, t_sample = 3, clock_div = 8;
           3  =>  user-specified length, t_sample and clock_div. */
#define ADC10_NSAMPLE 0x84 

extern app_t const adc_app;

#endif // ADC_H

