/*! \file spi.h
  \author Travis Goodspeed
  \brief Definitions for the SPI application.
*/

#ifndef SPI_H
#define SPI_H

#include "app.h"

#define SPI 0x01

//Pins and I/O
#if (platform == donbfet)
# define MOSI (1 << PA2)
# define MISO (1 << PA1)
# define SCK  (1 << PA0)
# define SS   (1 << PA3)
# define TST  (1 << PA4)
# define XRST (1 << PA5)
#else
# define MOSI BIT1
# define MISO BIT2
# define SCK  BIT3
# define TST  BIT0
# define RST  BIT6
#endif
//Apimotev2 SET/CLRRST needs to be on pin 21, so 2.1 -- just redefine RST to BIT0

#define SETMOSI SPIOUT|=MOSI
#define CLRMOSI SPIOUT&=~MOSI
#define SETCLK SPIOUT|=SCK
#define CLRCLK SPIOUT&=~SCK
#define READMISO (SPIIN&MISO?1:0)

//FIXME this should be defined by the platform.
#if (platform == donbfet)
# define SETTST PORTA|=(1 << PA4);
# define CLRTST PORTA&=~(1 << PA4);
# define SETRST PORTA|=(1 << PA5);
# define CLRRST PORTA&=~(1 << PA5);
#else
# define SETTST P4OUT|=TST
# define CLRTST P4OUT&=~TST
# define SETRST P2OUT|=RST
# define CLRRST P2OUT&=~RST
#endif

//! Set up the pins for SPI mode.
void spisetup();

//! Read and write an SPI byte.
unsigned char spitrans8(unsigned char byte);

//! Read a block to a buffer.
void spiflash_peekblock(unsigned long adr,
			unsigned char *buf,
			unsigned int len);


//! Read a block to a buffer. 32b Adr
void spiflash_peekblock32(unsigned long adr,
			unsigned char *buf,
			unsigned int len);


//! Write many blocks to the SPI Flash.
void spiflash_pokeblocks(unsigned long adr,
			 unsigned char *buf,
			 unsigned int len);


//! Enable SPI writing
void spiflash_wrten();

//! Read and write an SPI byte.
unsigned char spitrans8(unsigned char byte);
//! Grab the SPI flash status byte.
unsigned char spiflash_status();
//! Erase a sector.
void spiflash_erasesector(unsigned long adr);

extern app_t const spi_app;

#endif
