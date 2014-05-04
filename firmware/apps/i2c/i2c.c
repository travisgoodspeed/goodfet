/*! \file i2c.c
  \author Travis Goodspeed
  \brief I2C Master  
*/


//Higher level left to client application.

//Based upon a neighborly example at
//http://codinglab.blogspot.com/2008/10/i2c-on-avr-using-bit-banging.html

#include "platform.h"
#include "command.h"
#include "i2c.h"

#ifndef _GNU_ASSEMBLER_
#include <msp430.h>
#endif

//Pins and I/O
#include <jtag.h>

//! Handles an i2c command.
void i2c_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len);

// define the i2c app's app_t
app_t const i2c_app = {

	/* app number */
	I2C_APP,

	/* handle fn */
	i2c_handle_fn,

	/* name */
	"I2C",

	/* desc */
	"\tThe I2C app implements the i2c bus protocol thus\n"
	"\tturning your GoodFET into a USB-to-i2c adapter.\n"
};

#define I2CDELAY(x) delay(x<<4)


//2xx only, need 1xx compat code
#define SDA TDI
#define SCL TDO

#define SDAINPUT SPIDIR&=~SDA
#define SDAOUTPUT SPIDIR|=SDA
#define SCLINPUT SPIDIR&=~SCL
#define SCLOUTPUT SPIDIR|=SCL

#define PULLON SPIREN|=(SDA|SCL)
#define PULLOFF SPIREN&=~(SDA|SCL)

#define CLRSDA SPIOUT&=~SDA
#define SETSDA SPIOUT|=SDA
#define CLRSCL SPIOUT&=~SCL
#define SETSCL SPIOUT|=SCL

#define READSDA (SPIIN&SDA?1:0)
#define SETBOTH SPIOUT|=(SDA|SCL)

#define I2C_DATA_HI() SETSDA
#define I2C_DATA_LO() CLRSDA

#define I2C_CLOCK_HI() SETSCL
#define I2C_CLOCK_LO() CLRSCL

//#warning "Using internal resistors.  Won't work on 161x devices."

// Take control of the bus
void I2C_Take()
{
  I2C_CLOCK_HI();
  I2C_DATA_HI();
  SCLOUTPUT;
  SDAOUTPUT;
}

void I2C_Release()
{
  SDAINPUT;
  SCLINPUT;
}

//! Inits bitbanging port, must be called before using the functions below
void I2C_Init()
{
  I2C_Take();
  //PULLON;
  I2CDELAY(1);
}

// XXX This is never called...
void I2C_Exit()
{
  I2C_Release();
  PULLOFF;
}

//! Write an I2C bit.
void I2C_WriteBit( unsigned char c )
{
  if(c>0)
    I2C_DATA_HI();
  else
    I2C_DATA_LO();

  I2C_CLOCK_HI();
  I2CDELAY(1);

  I2C_CLOCK_LO();
  I2CDELAY(1);
}

//! Read an I2C bit.
unsigned char I2C_ReadBit()
{
  SDAINPUT;
  I2C_CLOCK_HI();
  
  unsigned char c = READSDA;
  if(c)
    I2C_DATA_HI();
  else
    I2C_DATA_LO();

  SDAOUTPUT;
  I2CDELAY(1);
  I2C_CLOCK_LO();
  I2CDELAY(1);

  return c;
}

unsigned char I2C_ReadBit_Wait()
{
  SDAINPUT;
  I2C_CLOCK_HI();
  
  unsigned int i = 0;
  unsigned char c = READSDA;

  while(c>0 && i<=35)
  {
    I2CDELAY(1);
    c = READSDA;
    i++;
  }

  if(c)
    I2C_DATA_HI();
  else
    I2C_DATA_LO();

  SDAOUTPUT;
  I2CDELAY(1);
  I2C_CLOCK_LO();
  I2CDELAY(1);

  return c?0:1;	// return true on ACK (0)
}

//! Send a START Condition
void I2C_Start()
{
  I2C_Take();	// XXX Should probably check to see if someone else is using the bus before we do this
  I2CDELAY(3);
  
  I2C_DATA_LO();
  I2CDELAY(3);
  
  I2C_CLOCK_LO();
  I2CDELAY(1);
}

//! Send a STOP Condition
void I2C_Stop()
{
  I2C_DATA_LO();
  I2CDELAY(3);

  I2C_CLOCK_HI();
  I2CDELAY(3);

  I2C_DATA_HI();
  I2CDELAY(1);
  I2C_Release();
}

//! write a byte to the I2C slave device
unsigned char I2C_Write( unsigned char c )
{
  char i;
  for (i=0;i<8;i++){
    I2C_WriteBit( c & 0x80 );
    c<<=1;
  }
  
  return I2C_ReadBit_Wait();
}

//! read a byte from the I2C slave device
unsigned char I2C_Read( unsigned char ack )
{
  unsigned char res = 0;
  char i;
  
  for (i=0;i<8;i++){
    res <<= 1;
    res |= I2C_ReadBit();  
  }
  
  if( ack > 0)
    I2C_WriteBit(0);
  else
    I2C_WriteBit(1);
  
  I2CDELAY(1);
  
  return res;
}

//! scans the bus to see if addr is in use
// Algorithm is taken from the BusPirate firmware
unsigned char I2C_Scan(unsigned char addr)
{
    unsigned char rv = 0;
    unsigned char c;

    I2C_Start(); // send start
    I2C_Write(addr); // send address
    c = I2C_ReadBit(); // look for ack
    if (c == 0) {
        cmddata[0] = addr;
        if ((addr & 1) == 0) {
            I2C_Read(0); // Read + NACK
        }
        rv = 1;
    }
    I2C_Stop();
    return rv;
}

//! Handles an i2c command.
void i2c_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len)
{
	unsigned char i;
	unsigned long l;
	switch(verb)
	{
	case READ:
		l = len;
		if(l > 0)					//optional parameter of length
			l=cmddata[0];
		if(!l)						//default value of 1
			l=1;
		I2C_Start();
		for(i=0; i < l; i++)
			cmddata[i]=I2C_Read(i<l?1:0);
		I2C_Stop();
		txdata(app,verb,l);
		break;
	case WRITE:
		I2C_Start();
		cmddata[0] = cmddata[0] << 1;
		for(i=0; i<len; i++) {
			if (!I2C_Write(cmddata[i]))		//if NACK
				break;
		}
		I2C_Stop();
		cmddata[0] = i;
		txdata(app,verb,1);
		break;
	case PEEK:
		l = cmddata[0];
		I2C_Start();
		unsigned char address = cmddata[1] << 1;
		I2C_Write(address);
		for(i=2; i < len; i++){
			I2C_Write(cmddata[i]);
		}
		I2C_Start();
		I2C_Write(address|1);				// spit out the target address again and flip the read bit
		I2CDELAY(1);	// XXX We should wait for clock to go high here XXX
		for(i=0; i < l; i++)
			cmddata[i]=I2C_Read(i+1<l?1:0);		// If the next i is still less than l, then ACK
		I2C_Stop();
		txdata(app,verb,l);
		break;
	case POKE:
		break;

	case START:
		I2C_Start();
		txdata(app,verb,0);
		break;
	case STOP:
		I2C_Stop();
		txdata(app,verb,0);
		break;
	case SETUP:
		I2C_Init();
		txdata(app,verb,0);
		break;
	case CMD_SCAN:
		txdata(app, verb, I2C_Scan(cmddata[0]));
		break;
	}
}
