/*! \file glitch.c
  \author Travis Goodspeed
  \brief Glitching Support for GoodFET20
  
  See the TI example MSP430x261x_dac12_01.c for usage of the DAC.
  This module sends odd and insufficient voltages on P6.6/DAC0
  in order to bypass security restrictions of target devices.
*/

#include "platform.h"
#include "command.h"
#include "glitch.h"

#include <msp430.h>

//! Handles a monitor command.
void glitch_handle_fn( uint8_t const app,
					   uint8_t const verb,
					   uint32_t const len);

// define the glitch app's app_t
app_t const glitch_app = {

	/* app number */
	GLITCH,

	/* handle fn */
	glitch_handle_fn,

	/* name */
	"GLITCH",

	/* desc */
	"\tThe GLITCH app adds support for doing glitch research.\n"
	"\tSee the TI example MSP430x261x_dac12_01.c for usage of the DAC.\n"
	"\tThis module sends odd and insufficient voltages on P6.6/DAC0\n"
	"\tin order to bypass security restrictions of target devices.\n"
};

//! Call this before the function to be glitched.
void glitchprime(){
#ifdef DAC12IR
  WDTCTL = WDTPW + WDTHOLD;             // Stop WDT
  
  glitchsetup();
  //_EINT();
  __eint();
  return;
#endif
}

//! Setup glitching.
void glitchsetup(){
#ifdef DAC12IR
  //Set GSEL high to disable glitching.
  
  //Normal voltage, use resistors instead of output.
  //P5DIR=0x80;   //ONLY glitch pin is output.
  P5DIR|=0x80;   //glitch pin is output.
  P5OUT|=0x80;  //It MUST begin high.
  //P5REN|=0x7F;  //Resistors pull high and low weakly.
  
  P6DIR|=BIT6+BIT5;
  P6OUT|=BIT6+BIT5;
  
  WDTCTL = WDTPW + WDTHOLD;             // Stop WDT
  TACTL = TASSEL1 + TACLR;              // SMCLK, clear TAR
  CCTL0 = CCIE;                         // CCR0 interrupt enabled
  CCR0 = glitchcount+0x10;              // Compare Value
  TACTL |= MC_2;                        // continuous mode.
#endif
}

// Timer A0 interrupt service routine
void __attribute__((interrupt(TIMERA0_VECTOR))) Timer_A (void){
  //This oughtn't be necessary, but glitches repeat without it.
  TACTL=0; //disable counter.
  
  
  P5OUT^=BIT7;//Glitch
  //asm("nop"); //delay deepens glitch.
  P5OUT^=BIT7;//Normal
  
  //This oughtn't be necessary, but glitches repeat without it.
  TACTL=0; //disable counter.
  
  //P5OUT^=BIT7;//Normal
  return;
}


u16 glitchcount=0;

//! Glitch an application.
void glitchapp(u8 app){
  debugstr("That app is not yet supported.");
}


//! Set glitching voltages.
void glitchvoltages(u16 gnd, u16 vcc){
  
  //debugstr("Set glitching voltages: GND and VCC");
  //debughex(gnd);
  //debughex(vcc);
  
  /** N.B., because this is confusing as hell.  As per Page 86 of
      SLAS541F, P6SEL is not what controls the use of the DAC0/DAC1
      functions on P6.6 and P6.5.  Instead, CAPD or DAC12AMP>0 sets
      the state.
  */
  
  #ifdef DAC12IR
  int i;
  ADC12CTL0 = REF2_5V + REFON;                  // Internal 2.5V ref on
  // Delay here for reference to settle.
  for(i=0;i!=0xFFFF;i++) asm("nop");
  DAC12_0CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
  DAC12_1CTL = DAC12IR + DAC12AMP_5 + DAC12ENC; // Int ref gain 1
  // 1.0V 0x0666, 2.5V 0x0FFF
  DAC12_0DAT = vcc; //high;
  DAC12_1DAT = gnd; //low;
  #endif 
}
//! Set glitching rate.
void glitchrate(u16 rate){
  glitchcount=rate;
}

//! Handles a monitor command.
void glitch_handle_fn( uint8_t const app,
					   uint8_t const verb,
					   uint32_t const len)
{
  switch(verb){
  case GLITCHVOLTAGES:
    glitchvoltages(cmddataword[0],
		   cmddataword[1]);
    txdata(app,verb,0);
    break;
  case GLITCHRATE:
    glitchrate(cmddataword[0]);
    txdata(app,verb,0);
    break;
  case GLITCHVERB:
    //FIXME parameters don't work yet.
    glitchprime();
    TAR=0; //Reset clock.
    handle(cmddata[0],cmddata[1],0);
    TACTL |= MC0;// Stop Timer_A;
    break;
  case GLITCHTIME:
    debugstr("Measuring start time.");
    __dint();//disable interrupts
    TACTL=0; //clear dividers
    TACTL|=TACLR; //clear config
    TACTL|=
      TASSEL_2 //smclk source
      | MC_2; //continuous mode.
    
    //perform the function
    silent++;//Don't want the function to return anything.
    TAR=0;
    handle(cmddata[0],cmddata[1],0);
    cmddataword[0]=TAR; //Return counter.
    silent--;
    debugstr("Measured start time.");
    debughex(cmddataword[0]);
    txdata(app,verb,2);
    break;
  case START:
    //Testing mode, for looking at the glitch waveform.
    glitchvoltages(0,0xFFF);//Minimum glitch, for noise test.
    //glitchvoltages(0,0);//Drop VCC
    //glitchvoltages(0xFFF,0xFFF);//Raise Ground
    P5OUT|=BIT7;//Normal
    P5DIR|=BIT7;
    while(1){
      P5OUT&=~BIT7;//Glitch
      //asm("nop"); //Not Necessary
      P5OUT|=BIT7;//Normal
      asm("nop");asm("nop");asm("nop");asm("nop");asm("nop");asm("nop");
      asm("nop");asm("nop");asm("nop");asm("nop");asm("nop");asm("nop");
    }
    txdata(app,verb,0);
    break;
  case STOP:
  case GLITCHAPP:
  default:
    debugstr("Unknown glitching verb.");
    txdata(app,NOK,0);
  }
}
