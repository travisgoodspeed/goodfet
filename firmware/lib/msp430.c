/*! \file msp430.c
  \author Travis Goodspeed
  \brief MSP430-generic functions.
*/


//Silently be empty if not an MSP430.
#ifdef MSP430


#include "platform.h"
#include "command.h"
#include "apps.h"
#include "glitch.h"

void led_init()
{
	PLEDDIR |= PLEDPIN;
	#ifdef PLED2OUT
	PLED2DIR |= PLED2PIN;
	#endif
	#ifdef PLED3OUT
	PLED3DIR |= PLED3PIN;
	#endif
}

//TODO define differently if needed for telos/apimote
void led_on()
{
	PLEDOUT |= PLEDPIN;
}
void led_off()
{
  PLEDOUT&=~PLEDPIN;
}
void led_toggle()
{
	PLEDOUT ^= PLEDPIN;
}

//LED2 and LED3 are only used by the telosb and apimote for now
void led2_on()
{
#ifdef PLED2OUT
    PLED2OUT &= ~PLED2PIN;
#endif
}
void led2_off()
{
#ifdef PLED2OUT
    PLED2OUT |= PLED2PIN;
#endif
}
void led3_on()
{
#ifdef PLED3OUT
    PLED3OUT &= ~PLED3PIN;
#endif
}
void led3_off()
{
#ifdef PLED3OUT
    PLED3OUT |= PLED3PIN;
#endif
}

//! Initialize MSP430 registers and all that jazz.
void msp430_init(){
	WDTCTL = WDTPW + WDTHOLD;					// Stop watchdog timer

	//LED out and on.
	led_init();
	led_off();

	/* P5.0 out and low; this is chosen for the PIC app (in which P5.0
	 is !MCLR) to ensure that an attached PIC chip, if present, is
	 immediately driven to reset state. A brief explanation of why this
	 is important follows.

	At least dsPIC33F and PIC24H --and very likely other 16-bit PIC
	families-- draw a large amount of current when running, especially
	when using a fast clock: from 60 mA up to approx. 90 mA.  If the
	PIC target begins to run before the client can request a new ICSP
	session, which requires much less current (e.g., less than 2 mA),
	then the MSP430 chip on the GoodFET will fail to start and the FTDI
	may have trouble communicating with the client.	The latter likely
	relates to the FTDI on-chip 3V3 regulator being specified up to
	only 50 mA. */


	//P5REN &= ~BIT0; //DO NOT UNCOMMENT.  Breaks GF1x support.

	//This will have to be cut soon.	Use pulling resistors instead.
	/*
	P5DIR |= BIT0;
	P5OUT &= ~BIT0;
	*/

	//Setup clocks, unique to each '430.
	msp430_init_dco();
	msp430_init_uart();

	//DAC should be at full voltage if it exists.
#ifdef DAC12IR
	//glitchvoltages(0xfff,0xfff);
	ADC12CTL0 = REF2_5V + REFON;					// Internal 2.5V ref on
	//for(i=0;i!=0xFFFF;i++) asm("nop"); //DO NOT UNCOMMENT, breaks GCC4
	DAC12_0CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
	DAC12_0DAT = 0xFFF; //Max voltage 0xfff
	DAC12_1CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
	DAC12_1DAT = 0x000; //Min voltage 0x000
#endif

	/** FIXME

	  This part is really ugly.  GSEL (P5.7) must be high to select
	  normal voltage, but a lot of applications light to swing it low
	  to be a nuissance.  To get around this, we assume that anyone
	  with a glitching FET will also have a DAC, then we set that DAC
	  to a high voltage.

	  At some point, each target must be sanitized to show that it
	  doesn't clear P5OUT or P5DIR.
	*/
	P5DIR|=BIT7; P5OUT=BIT7; //Normal Supply
	//P5DIR&=~BIT7; //Glitch Supply

	//Enable Interrupts.
	//eint();

}

//MSP430
#endif
