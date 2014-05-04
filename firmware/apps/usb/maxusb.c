/*! \file max3421.c
  \author Travis Goodspeed
  \brief SPI Driver for MAX342x USB Controllers
*/


#include "command.h"

#ifdef __MSPGCC__
#include <msp430.h>
#else
#include <signal.h>
#include <msp430.h>
#include <iomacros.h>
#endif

#include "maxusb.h"

#define MAXUSBAPPLICATION

#include "platform.h"


// define for the app list.
app_t const maxusb_app = {
	/* app number */
	MAXUSB,

	/* handle fn */
	maxusb_handle_fn,

	/* name */
	"MAXUSB",

	/* desc */
	"\tThis allows you to write USB Host or USB Device drivers for\n"
	"\t the MAX3421 and MAX3420 chips.\n"
};

//! Set up the pins for SPI mode.
void maxusb_setup(){
  SETSS;
  SPIDIR|=MOSI+SCK+BIT0; //BIT0 might be SS
  SPIDIR&=~MISO;
  P4DIR&=~TST; //TST line becomes interrupt input.
  P4DIR&=~BIT7; //GPX pin.
  P2DIR|=RST;
  DIRSS;
  
  
  //Setup the configuration pins.
  //This might need some delays.
  CLRRST; //Put the chip into RESET.
  SETSS;  //Deselect the chip, end any existing transation.
  SETRST; //Bring the chip out of RESET.
}



//! Handles a MAXUSB monitor command.
void maxusb_handle_fn( uint8_t const app,
		       uint8_t const verb,
		       uint32_t const len){
  unsigned long i;

  //Raise !SS to end transaction, just in case we forgot.
  SETSS;

  switch(verb){
  case READ:
  case WRITE:
    CLRSS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=spitrans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;

  case PEEK://TODO peek a register.
    debugstr("PEEK isn't implemented in MAXUSB");
    txdata(app,verb,0);
    break;

  case POKE://TODO poke a register.
    debugstr("POKE isn't implemented in MAXUSB");
    txdata(app,verb,0);
    break;
    
  case SETUP:
    maxusb_setup();
    txdata(app,verb,0);
    break;
  }
	
  //Raise !SS to end transaction, in case we forgot.
  SETSS;
}
