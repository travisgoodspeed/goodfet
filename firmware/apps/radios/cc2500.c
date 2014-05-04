/*! \file ccspi.c
  \author Jean-Michel Picod
  \brief Chipcon SPI CC2500

  Unfortunately, there is very little similarity between the CC2420
  and the CC2500, to name just two of the myriad of Chipcon SPI
  radios.  Auto-detection will be a bit difficult, but more to the
  point, all high level functionality must be moved into the client.
*/

//Higher level left to client application.

#include "platform.h"
#include "command.h"
#include <stdlib.h> //added for itoa

#include "cc2500.h"
#include "spi.h"

#define CC2500_MEM_READ		0x80
#define CC2500_MEM_BURST	0x40
#define CC2500_MEM_WRITE	0x00

#define RADIO_TX   SETCE
#define RADIO_RX   CLRCE

//! Handles a Chipcon SPI command.
void cc2500_handle_fn( uint8_t const app,
		      uint8_t const verb,
		      uint32_t const len);

// define the ccspi app's app_t
app_t const cc2500_app = {

	/* app number */
	CC2500,

	/* handle fn */
	cc2500_handle_fn,

	/* name */
	"CC2500",

	/* desc */
	"\tThe CC2500 app adds support for the Chipcon SPI register\n"
	"\tinterface for the CC2500 (and similar) chip.\n"
};

//! Set up the pins for CCSPI mode.
void cc2500setup(){
  SPIDIR&=~MISO;
  SPIDIR|=MOSI+SCK;
  DIRSS;
  DIRCE;

  msdelay(100);

  CLRCE;
  SETCE;

  //Begin a new transaction.
  CLRSS;
  SETSS;
}

//! Read and write an CCSPI byte.
u8 cc2500trans8(u8 byte){
  register unsigned int bit;
  //This function came from the CCSPI Wikipedia article.
  //Minor alterations.

  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;

    SETCLK;

    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }

  return byte;
}


//! Writes a register
u8 cc2500_regwrite(u8 reg, const u8 *buf, int len){
  CLRSS;

  if (len>1)
    reg |= CC2500_MEM_BURST;
  reg=cc2500trans8(reg|CC2500_MEM_READ);
  while(len--)
    cc2500trans8(*buf++);

  SETSS;
  return reg;//status
}
//! Reads a register
u8 cc2500_regread(u8 reg, u8 *buf, int len){
  CLRSS;

  if (len>1)
    reg|=CC2500_MEM_BURST;
  reg=cc2500trans8(reg|CC2500_MEM_WRITE);
  while(len--)
    *buf++=cc2500trans8(0);

  SETSS;
  return reg;//status
}

//! Handles a Chipcon SPI command.
void cc2500_handle_fn( uint8_t const app,
		      uint8_t const verb,
		      uint32_t const len){
  unsigned long i, nbyte;

  SETSS;
  cc2500setup();

  switch(verb){
  case PEEK:
  case READ:
    cmddata[0]|=CC2500_MEM_READ; //Set the read bit.
    //DO NOT BREAK HERE.
  case WRITE:
  case POKE:
    if (len > 2)
      cmddata[0] |= CC2500_MEM_BURST;
    CLRSS; //Drop !SS to begin transaction.
    for(i=0;i<len;i++)
      cmddata[i]=cc2500trans8(cmddata[i]);
    SETSS;  //Raise !SS to end transaction.
    txdata(app,verb,len);
    break;
  case SETUP:
    cc2500setup();
    txdata(app,verb,0);
    break;

  case CC2500_REPEAT_RX:
    while (1) {
      cc2500_handle_fn(app, CC2500_RX, 0);
    }
    break;

  case CC2500_RX:
    debugstr("RX is not functionning right now");
    txdata(app, verb, 0);
    break;

  case CC2500_TX:
    RADIO_TX; // Set option power amplificator to TX
    // FIXME: Flush FIFO first ?
    // Fill FIFO
    CLRSS;
    cc2500trans8(CC2500_TXFIFO | CC2500_MEM_BURST); // TX FIFO Burst
    for (i = 0; i < len; i++)
      cc2500trans8(cmddata[i]);
    SETSS; // Exit burst mode
    CLRSS;
    cc2500trans8(CC2500_STX); // Go to TX mode
    SETSS;
    txdata(app, verb, 0);
    break;

  case CC2500_RX_FLUSH:
    //Flush the buffer.
    CLRSS;
    cc2500trans8(CC2500_SIDLE);
    cc2500trans8(CC2500_SFLUSHRX);
    SETSS;
    txdata(app,verb,0);
    break;

  case CC2500_TX_FLUSH:
    //Flush the buffer.
    CLRSS;
    cc2500trans8(CC2500_SIDLE);
    cc2500trans8(CC2500_SFLUSHTX);
    SETSS;
    txdata(app,verb,0);
    break;

  default:
    debugstr("Not yet supported in CC2500");
    txdata(app,verb,0);
    break;
  }

}
