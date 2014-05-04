/*! \file twe.c
  \author EiNSTeiN_ <einstein@g3nius.org>
  \brief Atmel 2-wire EEPROM
*/

#include "command.h"

#include <signal.h>
#include <msp430.h>
#include <iomacros.h>

#include "twe.h"

#include "platform.h"

//! Handles a monitor command.
void spi_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len);

// define the spi app's app_t
app_t const twe_app = {

	/* app number */
	TWE,

	/* handle fn */
	twe_handle_fn,

	/* name */
	"2-wire EEPROM",

	/* desc */
	"\tThis app handles Atmel's 2-wire EEPROM protocol.\n"
};

// Transmit the START condition
void twe_start()
{
    SETSDA;
    
    SETSCL;
    delay_us(1);
    
    // high to low transision of SDA while SCL is high
    CLRSDA;
    delay_us(1);
    
    CLRSCL;
    delay_us(2);
    
    SETSDA;
  
}

// transmit the STOP condition
void twe_stop()
{
    CLRSDA;
    SETSCL;
    delay_us(1);
    
    // low to high transision of SDA while SCL is high
    SETSDA;
    delay_us(2);
    
    CLRSCL;
    delay_us(1);
}

//! Write 8 bits and read 1
unsigned char twe_tx(unsigned char byte){
  unsigned int bit;
  
  for (bit = 0; bit < 8; bit++) {
    delay_us(15);
    
    /* write SDA on trailing edge of previous clock */
    if (byte & 0x80)
      SETSDA;
    else
      CLRSDA;
    byte <<= 1;
    
    SETSCL;
    delay_us(1);
    CLRSCL;
  }
  
  // 9th bit is ACK
  SPIDIR &= ~SDA;
  SPIREN |= SDA;  /* as per datasheet, SDA must be pulled high externally */
  SPIOUT |= SDA;
  SETSCL;
  delay_us(1);
  bit = (SPIIN & SDA) ? 1 : 0;
  delay_us(1);
  CLRSCL;
  delay_us(10);
  SPIOUT &= ~SDA;
  SPIREN &= ~SDA;
  SPIDIR |= SDA;
  
  if(bit) {
    debugstr("not acked :s");
  }
  
  return bit;
}

//! Read 8 bits, optionally acking it
unsigned char twe_rx(unsigned int ack){
  unsigned int rd = 0;
  unsigned int bit = 0;
  
  SPIDIR &= ~SDA;
  SPIREN |= SDA; /* as per datasheet, SDA must be pulled high externally */
  SPIOUT |= SDA;
  
  for (bit = 0; bit < 8; bit++) {
    delay_us(10);
    SETSCL;
    delay_us(1);
    if(SPIIN & SDA)
        rd |= 1 << (7-bit);
    delay_us(1);
    CLRSCL;
  }
  
  SPIOUT &= ~SDA;
  SPIREN &= ~SDA;
  SPIDIR |= SDA;
  
  if(ack) {
    // 9th bit is ACK
    CLRSDA;
      
    SETSCL;
    delay_us(15);
    CLRSCL;
    delay_us(15);
  }
  
  return rd;
}

//! Read a block to a buffer.
void twe_peekblock(uint8_t const app,
              uint8_t const verb,
              uint16_t adr,
              uint32_t len)
{
  unsigned char i;
  
  // start command / write
  twe_start();
  twe_tx(0xa0); // preamble=1010, device adr=000, write=0
  
  // output address bytes
  twe_tx((adr >> 8) & 0xff);
  twe_tx(adr & 0xff);
  
  // start command / read
  twe_start();
  twe_tx(0xa1); // preamble=1010, device adr=000, read=1
  
  //Send reply header
  txhead(app, verb, len);
  
  for(i=0;i<len;i++)
    serial_tx(twe_rx(i != (len-1)));
  
  twe_stop();
  
  return;
}

//! Read a block to a buffer.
void twe_pokeblock(uint16_t adr,
              uint8_t *buf,
              uint32_t len)
{
  unsigned char i;
  // start command / write
  twe_start();
  twe_tx(0xa0); // preamble=1010, device adr=000, write=0
  
  // output address bytes
  twe_tx((adr >> 8) & 0xFF);
  twe_tx(adr & 0xFF);
  
  for(i=0;i<len;i++)
    twe_tx(buf[i]);
  
  twe_stop();
  
  return;
}

//! Set up the pins for SPI mode.
void twe_setup()
{
  int i;
  
  SETSDA; // normal position
  CLRSCL; // normal position
  SPIDIR |= SDA | SCL;
  
  twe_start();
  
  SETSDA;
  for(i=0;i<9;i++) {
    SETSCL;
    delay_us(15);
    CLRSCL;
    delay_us(15);
  }
  
  twe_start();
  twe_stop();
}

//! Handles a monitor command.
void twe_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len)
{
  uint16_t adr;
  switch(verb)
  {
    case PEEK: //Grab 128 bytes from an SPI Flash ROM
      adr = cmddataword[0];
      twe_setup();
      twe_peekblock(app, verb, adr, 128);
      break;

    //~ case POKE: //Grab 128 bytes from an SPI Flash ROM
      //~ debugstr("reading");
      //~ twe_pokeblock(cmddata, len);
      //~ break;

    case SETUP:
      twe_setup();
      txdata(app,verb,0);
      break;
  }
}
