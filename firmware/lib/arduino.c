/*! \file arduino.c
  \author Travis Goodspeed
  \brief Arduino platform support.
*/

#include "platform.h"
#ifdef ARDUINO

#include <avr/interrupt.h>
#include <util/delay.h>

//! Arduino setup code.
void arduino_init(){
  //LED port as output.
  DDRB = 0xFF;
  
  //Disabled interrupts.
  cli();
  
  avr_init_uart0();
}

#endif
