#include <cc1110.h>
#include "cc1110-ext.h"

//! Start the crystal oscillator at 26MHz.
void main(){
  // Turn both high speed oscillators on
  SLEEP &= ~SLEEP_OSC_PD;
  // Wait until xtal oscillator is stable
  while( !(SLEEP & SLEEP_XOSC_S) ); 

  
  
  // Select xtal osc, 26 MHz
  // This doesn't work for the USB dongles.
  CLKCON = 
    (CLKCON & ~(CLKCON_CLKSPD | CLKCON_OSC))
    | CLKSPD_DIV_1;
  
  
  /*
  //Needed for CC1111?
  CLKCON = 
    (CLKCON & ~(CLKCON_CLKSPD | CLKCON_OSC))
    | CLKSPD_DIV_2;
  */
  
  // Wait for change to take effect
  while (CLKCON & CLKCON_OSC); 
  // Turn off the RC osc.
  SLEEP |= SLEEP_OSC_PD; 
  
  HALT;
}
