/*! \file owe.h
  \author Andreas Droescher
  \brief Dallas 1-wire bus protocol functions.
*/

#include "platform.h"
#include "command.h"
#include "owe.h"

#ifndef _GNU_ASSEMBLER_
#include <msp430.h>
#endif

//Pins and I/O
#include <jtag.h>

//! Handles an 1-wire command.
void owe_handle_fn( uint8_t const app,
                        uint8_t const verb,
                        uint32_t const len);

// define the owe app's app_t
app_t const owe_app = {

	/* app number */
	OWE_APP,

	/* handle fn */
	owe_handle_fn,

	/* name */
	"1-wire",

	/* desc */
	"\tThe 1-wire app implements the Dallas/Maxim 1-wire bus\n"
	"\tprotocol turning your GoodFET into a USB-to-1-wire adapter.\n"
};

void setup() {
	prep_timer();
	P4SEL  =  0;    //GPIO
	P4DIR  =  0;    //IN
	P4REN  =  BIT0; //Enable Resistor
	P4OUT  =  BIT0; //HI
		
	// Reset Communication
	delay_ms(250);	
}

int initialize() {
	// Generate Reset Pulse
	P4OUT &= ~BIT0;  //LOW
    delay_us(500);
	P4OUT |=  BIT0;  //HI
	
	// Check for response
	delay_us(30);
	int r = (P4IN & BIT0);
	delay_us(470);
		
	return r;
}

void sendbit(int b)  {
	// Initiate Write
	P4OUT &= ~BIT0;    //LOW
    delay_us(12);
	if(b) {
		P4OUT |= BIT0; //HI
	}
    delay_us(53);
	P4OUT |= BIT0;     //HI
	
	// Recovery Time
	delay_us(5);
}

void sendbyte(uint8_t b) {
	int i;
	for(i = 0; i<8;i++) {
		sendbit(b & 0x01);
		b = b>>1;
	}
}

int receivebit() {
	// Initiate Read
	P4OUT &= ~BIT0;    //LOW
    delay_us(2);
	P4OUT |= BIT0;     //HI

	// Read
    delay_us(5);	
	int r = (P4IN & BIT0);
	
	// Recovery Time
	delay_us(60);

	return r;
}

uint8_t receivebyte() {
	int i = 0; uint8_t r = 0;
	for(i = 0; i<8;i++) {
		r |= (receivebit() & BIT0) <<i;
	}
	return r;
}

//! Handles an  1-wire command.
void owe_handle_fn(uint8_t  const app,
                   uint8_t  const verb,
                   uint32_t const len)
{
	switch(verb) {
		case 0x10:
			setup();
			txdata(app,0,0);
			break;
		case 0x20:
			if(initialize() != 0) {
				txdata(app,1,0);
			} else {
				txdata(app,0,0);
			}
			break;
		case 0x01:
			sendbyte(cmddata[0]);
			txdata(app,0,0);
			break;
		case 0x00:
			cmddata[0] = receivebyte();	
			txdata(app,0,1);
			break;
		default:
			txdata(app,1,0);
			break;
	}
}
