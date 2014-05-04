/*! \file adc.c

	\author Scott Livingston

	\brief Simple A/D sampling of a GoodFET pin.  Currently assumes
	       x2274 chip, on a GoodFET31 board.

	\date September 2010
*/

#include "platform.h"
#include "command.h"
#include "adc.h"

//! Handle an ADC10 command; currently assumes x2274, on a GoodFET31 board.
void adc_handle_fn( uint8_t const app,
					  uint8_t const verb,
					  uint32_t const len);

// define the adc app's app_t
app_t const adc_app = {

	/* app number */
	ADC,

	/* handle fn */
	adc_handle_fn,

	/* name */
	"ADC",

	/* desc */
	"\tThe ADC app adds simple A/D sampling of a GoodFET pin.\n"
	"\tCurrently assumes x2274 chip, on a GoodFET31 board.\n"
};

void init_adc10()
{
	ADC10CTL0 = ADC10DISABLE;
	ADC10CTL0 = REFON | REF2_5V | ADC10ON; // internal reference, at 2.5V
	ADC10CTL1 = INCH_5 | ADC10SSEL_2; // input A5; using MCLK as clock source.
	ADC10AE0 = 1<<5; // enable channel A5
	ADC10SA = 0x200; // Start at bottom of RAM (i.e. lowest address).
}

void uninit_adc10()
{
	ADC10CTL0 = ADC10DISABLE;
	ADC10CTL0 = ADC10CTL1 = 0x0000;
}


//! Handle an ADC10 command; currently assumes x2274, on a GoodFET31 board.
void adc_handle_fn( uint8_t const app,
					  uint8_t const verb,
					  uint32_t const len)
{
	u16 sample;
	u16 actual_N;

	switch (verb) {

	case ADC10_INIT:
		init_adc10();
		txdata(app,verb,0);
		break;

	case ADC10_UNINIT:
		uninit_adc10();
		txdata(app,verb,0);
		break;

	case ADC10_1SAMPLE: //! Capture and return a single sample.
		sample = sample_adc10();
		*cmddata = sample & 0xff;
		*(cmddata+1) = sample >> 8;
		txdata(app,verb,2);
		break;

	case ADC10_NSAMPLE: //! Capture and return a sequence, with constanst Sps.
		if (*cmddata == 0)
			*cmddata = 0xff; // Max length
		/*if (len == 0) {
			actual_N = nsamples_adc10( 0xff, 3, 8 ); 
		} else if (len == 1) {
			actual_N = nsamples_adc10( *cmddata, 3, 8 );
			} else {*/
			actual_N = nsamples_adc10( *cmddata, *(cmddata+1), *(cmddata+2) );
//		}
		txdata( app, verb, actual_N*2 );
		break;

	default:
		debugstr( "Verb unimplemented in ADC10 application." );
		txdata(app,NOK,0);
		break;

	}
}


u16 sample_adc10()
{
	// We assume the ADC10 module has already been initialized.
	u16 result;
	u16 ctl0_start = ADC10CTL0;

	ADC10CTL0 |= ADC10SHT_3; /* Switch to longest sample-and-hold time
														  (i.e. 64 ticks), to increase likelihood
														  of success given we are only taking a
														  single sample here. */
	ADC10CTL0 |= 0x0003; // ENC | ADC10SC
	while (!(ADC10CTL0 & ADC10IFG)) ;
	result = ADC10MEM;
	
	ADC10CTL0 = ctl0_start; /* Return ADC10 control register to original
													   state, at calling of this function. */
	return result;
}


u16 nsamples_adc10( u8 N_count, u8 t_sample, u8 clock_div )
{
	u16 ctl0_start;
	u16 ctl1_start;

	//while (ADC10BUSY) ; // Wait till any pending operation completes.

	ctl0_start = ADC10CTL0;
	ctl1_start = ADC10CTL1; // Save control registers states.
	
	if (N_count > (CMDDATALEN-4)/2) { // Bound number of samples to be obtained here.
		N_count = (CMDDATALEN-4)/2;
	}
	clock_div--; // Place in form appropriate for control register

	// Additional preparations of ADC10
	ADC10CTL0 |= (t_sample&0x3)<<11 | MSC;
	ADC10CTL1 |= (clock_div&0x7)<<5
		| ADC10SSEL_2 // source from MCLK (should be 16 MHz),
		| CONSEQ_2; // repeat-single-channel mode.

	// Setup DTC (to make acquisition of block of samples easy/reliable)
	ADC10DTC0 = 0x0000;
	ADC10DTC1 = N_count;
	ADC10SA = cmddata;

	ADC10CTL0 |= 0x0003; // ENC | ADC10SC

	while (!(ADC10CTL0 & ADC10IFG)) ;
	
	ADC10CTL0 = ctl0_start; // Restore control registers
	ADC10CTL1 = ctl1_start;
	ADC10DTC1 = 0x0000; // ...and disable DTC

	return N_count;
}
