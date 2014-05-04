/*! \file smartcard.c
  \author Travis Goodspeed
  \brief Smartcard and SIM application.
  
  This module allows for communication with smart cards and SIM cards.
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"
#include "smartcard.h"

//! Handles a monitor command.
void smartcard_handle_fn( uint8_t const app,
						  uint8_t const verb,
						  uint32_t const len);

// define the smartcard app's app_t
app_t const smartcard_app = {

	/* app number */
	SMARTCARD,

	/* handle fn */
	smartcard_handle_fn,

	/* name */
	"SMARTCARD",

	/* desc */
	"\tThe SMARTCARD app allows for communication with smart\n"
	"\tcards and SIM cards.\n"
};


//TDO/P5.2 is Data

//Read a bit.
#define SCIN (P5IN&BIT2)
//Set I/O direction.
#define SCINPUT (P5DIR&=~BIT2)
#define SCOUTPUT (P5DIR|=BIT2)
//Set data value.
#define SCH (P5OUT|=BIT2)
#define SCL (P5OUT&=~BIT2)

//Clock.
#define SCTICK (P5OUT|=BIT3)
#define SCTOCK (P5OUT&=~BIT3)


//! Setup the smart card mode.
void smartcardsetup(){
  P5DIR|=BIT3;
  P2DIR|=RST;
  msdelay(100);
}

u16 sctime=0, foo=0;

//! Handles a monitor command.
void smartcard_handle_fn( uint8_t const app,
						  uint8_t const verb,
						  uint32_t const len)
{
  switch(verb){
  case SETUP:
    smartcardsetup();
    break;
  case START:
    smartcardsetup();
    debugstr("Reseting card");
    SCINPUT;
    
    CLRRST;
    SCTICK;
    SCTOCK;
    SCTICK;
    SCTOCK;
    delay(500);
    SETRST;
    
    while(1){
      sctime++;
      SCTICK;
      delay(5);
      SCTOCK;
      
      led_toggle();
      if(SCIN!=foo){
	foo=SCIN;
      }
      if(sctime%0x1000==0)
	debughex(foo);
    }
    break;
  case STOP:
  default:
    debugstr("Unknown smartcard verb.");
    txdata(app,NOK,0);
  }
}
