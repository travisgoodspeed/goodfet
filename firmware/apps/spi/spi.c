/*! \file spi.c
  \author Travis Goodspeed
  \brief SPI Master
*/

//Higher level left to client application.


#include "command.h"

#ifdef __MSPGCC__
#include <msp430.h>
/* #else */
/* #include <signal.h> */
/* #include <msp430.h> */
/* #include <iomacros.h> */
#endif

#include "spi.h"

#define SPIAPPLICATION

#include "platform.h"

//! Handles a monitor command.
void spi_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len);

// define the spi app's app_t
app_t const spi_app = {

	/* app number */
	SPI,

	/* handle fn */
	spi_handle_fn,

	/* name */
	"SPI",

	/* desc */
	"\tThe SPI app handles the SPI bus protocol, turning\n"
	"\tyour GoodFET into a USB-to-SPI adapter.\n"
};

//This could be more accurate.
//Does it ever need to be?
#define SPISPEED 0
#define SPIDELAY(x) delay(x)


//! Set up the pins for SPI mode.
void spisetup(){
  SETSS;
  SPIDIR|=MOSI+SCK+BIT0; //BIT0 might be SS
  SPIDIR&=~MISO;
  DIRSS;
  DIRCE;

  //Begin a new transaction.

  CLRSS;
  SETSS;
}


//! Read and write an SPI byte.
unsigned char spitrans8(unsigned char byte){
  register unsigned int bit;
  //This function came from the SPI Wikipedia article.
  //Minor alterations.

  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;

    //SPIDELAY(100);
    SETCLK;
    //SPIDELAY(100);

    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }
  return byte;
}


//! Enable SPI writing
void spiflash_wrten(){
  SETSS;
  /*
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x04);//Write Disable
  SETSS;  //Raise !SS to end transaction.
  */
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x06);//Write Enable
  SETSS;  //Raise !SS to end transaction.
}


//! Grab the SPI flash status byte.
unsigned char spiflash_status(){
  unsigned char c;
  SETSS;  //Raise !SS to end transaction.
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x05);//GET STATUS
  c=spitrans8(0xFF);
  SETSS;  //Raise !SS to end transaction.
  return c;
}


//! Grab the SPI flash status byte.
void spiflash_setstatus(unsigned char c){
  SETSS;
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x01);//SET STATUS
  spitrans8(c);
  SETSS;  //Raise !SS to end transaction.
  //return c;
}

//! Set SPI flash status flags.
void spiflash_setstatusflags(unsigned char s, unsigned char preserve_mask){
  unsigned char cs; // Current status
  SETSS;
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x05);//GET STATUS
  cs=spitrans8(0xFF);

  cs = (cs&preserve_mask)|(s&(~preserve_mask));
  SETSS;  //Raise !SS to end transaction.
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x01);//SET STATUS
  spitrans8(cs);
  SETSS;  //Raise !SS to end transaction.
  //return c;
}


//! Read a block to a buffer.
void spiflash_peekblock(unsigned long adr,
			unsigned char *buf,
			unsigned int len){
  unsigned char i;

  SETSS;
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x03);//Flash Read Command

  //Send address
  spitrans8((adr&0xFF0000)>>16);
  spitrans8((adr&0xFF00)>>8);
  spitrans8(adr&0xFF);

  for(i=0;i<len;i++)
    buf[i]=spitrans8(0);
  SETSS;  //Raise !SS to end transaction.
}

//! Read a block to a buffer.
void spiflash_pokeblock(unsigned long adr,
			unsigned char *buf,
			unsigned int len){
  unsigned int i;

  SETSS;

  //if(len!=0x100)
  //  debugstr("Non-standard block size.");

  while(spiflash_status()&0x01);//minor performance impact

  spiflash_setstatus(0x02);
  spiflash_wrten();

  //Are these necessary?
  //spiflash_setstatus(0x02);
  //spiflash_wrten();

  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x02); //Poke command.

  //Send address
  spitrans8((adr&0xFF0000)>>16);
  spitrans8((adr&0xFF00)>>8);
  spitrans8(adr&0xFF);

  for(i=0;i<len;i++)
    spitrans8(buf[i]);
  SETSS;  //Raise !SS to end transaction.

  while(spiflash_status()&0x01);//minor performance impact
  return;
}


//! Write many blocks to the SPI Flash.
void spiflash_pokeblocks(unsigned long adr,
			 unsigned char *buf,
			 unsigned int len){
  long off=0;//offset of this block
  int blen;//length of this block
  SETSS;

  while(off<len){
    //calculate block length
    blen=(len-off>0x100?0x100:len-off);
    //write the block
    spiflash_pokeblock(adr+off,
		       buf+off,
		       blen);
    //add offset
    off+=blen;
  }
}



//! Peek some blocks.
void spiflash_peek(unsigned char app,
		   unsigned char verb,
		   unsigned long len){
  unsigned int i;
  CLRSS; //Drop !SS to begin transaction.
  spitrans8(0x03);//Flash Read Command
  len=3;//write 3 byte pointer
  for(i=0;i<len;i++)
    spitrans8(cmddata[i]);

  //Send reply header
  len=0x1000;
  txhead(app,verb,len);

  while(len--)
    serial_tx(spitrans8(0));

  SETSS;  //Raise !SS to end transaction.
}


//! Erase a sector.
void spiflash_erasesector(unsigned long adr){
  //debugstr("Erasing a 4kB sector.");

  //Write enable.
  spiflash_wrten();

  //Begin
  CLRSS;

  //Second command.
  spitrans8(0x20);
  //Send address
  spitrans8((adr&0xFF0000)>>16);
  spitrans8((adr&0xFF00)>>8);
  spitrans8(adr&0xFF);

  SETSS;
  while(spiflash_status()&0x01);//while busy
  //debugstr("Erased.");
}


//! Wake an EM260 Radio
void em260_wake(){
  //debugstr("Waking EM260.");
  #define RST BIT6
  P2DIR|=RST;
  SETRST;
  delay(1024);

  CLRRST;//Wake chip.
  while(P4IN&1);
  SETRST;//Woken.
  //debugstr("EM260 is now awake.");
  delay(1024);  //DO NOT REMOVE, fails without.
}
//! Handle an EM260 exchange.
void spi_rw_em260(u8 app, u8 verb, u32 len){
  unsigned long i;
  u8 lastin;

  P4DIR=0; //TODO ASAP remove P4 references.
  P4OUT=0xFF;
  //P4REN=0xFF;

  //See GoodFETEM260.py for details.
  //The EM260 requires that the host wait for the client.

  /*
    if((~P4IN)&1)
    debugstr("Detected HOST_INT.");
  */

  em260_wake();


  SETMOSI; //Autodetected SPI mode.
  CLRSS; //Drop !SS to begin transaction.
  //Host to slave.  Ignore data.
  for(i=0;i<len;i++){
    lastin=spitrans8(cmddata[i]);
    if(lastin!=0xFF){
      //debugstr("EM260 transmission interrupted.");
      cmddata[0]=lastin;
      goto response;
    }
  }
  //debugstr("Finished transmission to EM260.");

  //Wait for nHOST_INT to drop.
  i=0xffff;

  /*
  while(P4IN&1
	&& --i
	)
    spitrans8(0xFF);
  */
  while((cmddata[0]=spitrans8(0xFF))==0xFF
	&& --i);

  if(!i)
    debugstr("Gave up on host interrupt.");

 response:
  len=1;
  while(
	(cmddata[len++]=spitrans8(0xFF))!=0xA7
	);
  if(cmddata[0]==0xFE)
    while(len<cmddata[1]+3)
      cmddata[len++]=spitrans8(0xFF);
  SETSS;  //Raise !SS to end transaction.

  txdata(app,verb,len);
  return;
}

//! Handles a monitor command.
void spi_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len)
{
	unsigned long i, l;

	//Raise !SS to end transaction, just in case we forgot.
	SETSS;
	//spisetup();

	switch(verb)
	{
	case READ:
	case WRITE:
		CLRSS; //Drop !SS to begin transaction.
		for(i=0;i<len;i++)
		cmddata[i]=spitrans8(cmddata[i]);
		SETSS;  //Raise !SS to end transaction.
		txdata(app,verb,len);
		break;

	case SPI_RW_EM260:  //SPI exchange with an EM260
		spi_rw_em260(app,verb,len);
		break;

	case SPI_JEDEC://Grab 3-byte JEDEC ID.
		CLRSS; //Drop !SS to begin transaction.
		spitrans8(0x9f);
		l=3;  //Length is variable in some chips, 3 minimum.
		for(i = 0; i < l; i++)
			cmddata[i]=spitrans8(cmddata[i]);
		txdata(app,verb,len);
		SETSS;  //Raise !SS to end transaction.
		break;

	case SPI_ZENSYS_ENABLE:
		CLRTST; // power off
		msdelay(10);
		// Switch MISO to OUT
		SPIDIR |= MISO;
		CLRSS;
		CLRCLK;
		CLRMOSI;
		SPIOUT &= ~MISO;
		SETTST; // power on
		msdelay(20);
		// Set MISO back to IN
		SPIDIR &= ~MISO;
		// Transmit
		for (i = 0; i < len; i++)
			cmddata[i] = spitrans8(cmddata[i]);
		SETSS;
		txdata(app, verb, 4);
		break;

	case SPI_ZENSYS_WRITE3_READ1:
		CLRSS;
		for (i = 0; i < 3; i++)
			spitrans8(cmddata[i]);
		delay(5);  // wait for data to be ready
		cmddata[0] = spitrans8(cmddata[3]);
		SETSS;
		txdata(app, verb, 1);
		break;

	case SPI_ZENSYS_WRITE2_READ2:
		CLRSS;
		for (i = 0; i < 2; i++)
			spitrans8(cmddata[i]);
		delay(5); // wait for data to be ready
		cmddata[0] = spitrans8(cmddata[2]);
		cmddata[1] = spitrans8(cmddata[3]);
		SETSS;
		txdata(app, verb, 2);
		break;

	case PEEK://Grab 128 bytes from an SPI Flash ROM
		spiflash_peek(app,verb,len);
		break;

	case POKE://Poke up bytes from an SPI Flash ROM.
		spiflash_pokeblocks(cmddatalong[0],//adr
		cmddata+4,//buf
		len-4);//len
		txdata(app,verb,0);
		break;

	case SPI_ERASE://Erase the SPI Flash ROM.
		spiflash_wrten();
		CLRSS; //Drop !SS to begin transaction.
		spitrans8(0xC7);//Chip Erase
		SETSS;  //Raise !SS to end transaction.

		while(spiflash_status()&0x01)//while busy
			led_toggle();
		led_off();

		txdata(app,verb,0);
		break;

	case SETUP:
		spisetup();
		txdata(app,verb,0);
		break;
	}
}
