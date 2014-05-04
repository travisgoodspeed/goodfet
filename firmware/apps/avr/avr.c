/*! \file avr.c
  \author Travis Goodspeed
  \brief AVR SPI Programmer
*/

#include "platform.h"
#include "command.h"


#include "avr.h"
//#include "glitch.h"
//
//! Handles an AVR command.
void avr_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len);

// define the jtag app's app_t
app_t const avr_app = {

	/* app number */
	XAVR,

	/* handle fn */
	avr_handle_fn,

	/* name */
	"AVR",

	/* desc */
	"\tThe AVR app adds support for debugging AVR based devices.\n"
};

//! Setup the AVR pins.
void avrsetup(){
  spisetup();
}

//! Initialized an attached AVR.
void avrconnect(){
  //set I/O pins
  avrsetup(); //Cut this?

  SETSS;
  //delay(50);

  //Pulse !RST (SS) at least twice while CLK is low.
  CLRCLK;
  CLRSS;
  //delay(5);

  SETSS;
  CLRCLK;
  //delay(5);
  CLRSS;
  //delay(5);

  //Enable programming
  avr_prgen();
}

//! Read and write an SPI byte with delays.
u8 avrtrans8(u8 byte){
  register u16 bit;
  //This function came from the SPI Wikipedia article.
  //Minor alterations.

  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;

    delay(2);
    SETCLK;

    /* read MISO on trailing edge */
    byte |= READMISO;
    delay(2);
    CLRCLK;
  }

  return byte;
}

//! Perform a 4-byte exchange.
u8 avrexchange(u8 a, u8 b, u8 c, u8 d){
  avrtrans8(a);
  avrtrans8(b);
  if(avrtrans8(c)!=b){
    //debugstr("AVR sync error, b not returned as c.");
    //Reconnect here?
  }
  return avrtrans8(d);
}

//! Enable AVR programming mode.
void avr_prgen(){
  avrexchange(0xAC, 0x53, 0, 0);
}

//! Is the AVR ready or busy?
u8 avr_isready(){
  return avrexchange(0xF0, 0, 0, 0);
}

//! Read AVR device code.
u8 avr_sig(u8 i){
  return avrexchange(0x30, //Read signature byte
	      0x00,
	      i&0x03,      //sig adr
	      0x00         //don't care.
	      );
}

//! Erase an AVR device
void avr_erase(){
  avrexchange(0xAC, 0x80, 0, 0);
}

//! Read lock bits.
u8 avr_lockbits(){
  return avrexchange(0x58, 0, 0, 0);
}
//! Write lock bits.
void avr_setlock(u8 bits){
  avrexchange(0xAC,0xE0,0x00,
	      bits);
}

//! Read a byte of EEPROM.
u8 avr_peekeeprom(u16 adr){
  return avrexchange(0xA0, adr>>8, adr&0xFF, 0);
}
//! Read a byte of EEPROM.
u8 avr_pokeeeprom(u16 adr, u8 val){
  return avrexchange(0xC0, adr>>8, adr&0xFF, val);
}

//! Read a byte of Flash
u8 avr_peekflash(u16 adr){
  u16 a=adr>>1;
  if(adr&1) //high byte
    return avrexchange(0x28,a>>8,a&0xff,0);
  else      //low byte
    return avrexchange(0x20,a>>8,a&0xff,0);
}

void avr_bulk_load(u16 start, u16 len, u8 *data) {
  u16 adr;
  for (adr = 0; adr < len; adr++) {
    u16 a = adr + start;
    avrexchange((adr & 1) ? 0x48 : 0x40,
		a >> 9,
		(a >> 1) & 0xff,
		data[adr]);
  }
}

//! Handles an AVR command.
void avr_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len)
{
  unsigned long i, l;
  unsigned int at;

  /*
  if(!avr_isready() && connected)
    debugstr("AVR is not yet ready.");
  */

  switch(verb){
  case READ:
  case WRITE:
    for(i=0;i<len;i++)
      cmddata[i]=avrtrans8(cmddata[i]);
    txdata(app,verb,len);
    break;
  case SETUP:
    avrsetup();
    txdata(app,verb,0);
    break;
  case START:
    avrconnect();
    txdata(app,verb,0);
    break;//Used to fall through here.
  case STOP:
    SETSS;
    txdata(app, verb, 0);
  case AVR_PEEKSIG:
    for(i=0;i<4;i++)
      cmddata[i]=avr_sig(i);
    txdata(app,verb,4);
    break;
  case AVR_ERASE:
    avr_erase();
    txdata(app,verb,0);
    break;
  case AVR_PEEKLOCK:
    cmddata[0]=avr_lockbits();
    txdata(app,verb,1);
    break;
  case AVR_POKELOCK:
    avr_setlock(cmddata[0]);
    txdata(app,verb,0);
    break;
  case AVR_POKEEEPROM:
    avr_pokeeeprom(cmddataword[0], cmddata[2]);
    //no break here.
  case AVR_PEEKEEPROM:
    cmddata[0]=avr_peekeeprom(cmddataword[0]);
    txdata(app,verb,1);
    break;
  case AVR_BULKLOAD:
    if (len < 3) {
      debugstr("Length too short");
      txdata(app, NOK, 0);
    } else {
      at = cmddataword[0];
      avr_bulk_load(at, len - 2, cmddata + 2);
      txdata(app, verb, 0);
    }
    break;
  case PEEK:
    //cmddata[0]=avr_peekflash(cmddataword[0]);
    //txdata(app,verb,1);
    at=cmddataword[0];

    //Fetch large blocks for bulk fetches,
    //small blocks for individual peeks.
	l = len;
    if(l>2){
      l=(cmddataword[1]);//always even.
    }else{
      l=1;
    }
    txhead(app,verb,l);
    for(i=0;i<l;i++){
      serial_tx(avr_peekflash(at++));
    }
    break;
  case POKE:
  default:
    debugstr("Verb unimplemented in AVR application.");
    txdata(app,NOK,0);
    break;
  }
}

