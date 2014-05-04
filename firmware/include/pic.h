/*! \file dspic33f.h

  \author Scott Livingston

  \brief Definitions for the dsPIC33F programmer application. Note
         that the programming for dsPIC33F/PIC24H chips is
         non-standard 2-wire SPI; hence, I do not use the existing
         GoodFET SPI routines.

  \date March-June 2010

*/

#ifndef PIC_H
#define PIC_H

#include "app.h"

#define PIC 0x34

/*! Magic, device family specific constants (these are drawn from the
    dsPIC33F/PIC24H Flash Programming Specification). Note that the
    ICSP key is in bit-reversed order, since it is the only thing that
    is sent MSb first (hence, we flip the bit order and use our usual
    LSb-first routines).

    Per the dsPIC33F/PIC24H and PIC24F flash programming
    specifications, the ICSP key is 0x4D434851. */
#define ICSP_KEY_LOW 0xC2B2
#define ICSP_KEY_HIGH 0x8A12
#define APPID_ADDR 0x8007F0

//! I/O (pin level); follows spi.h
#define PGD BIT1
#define PGC BIT3
#define MCLR BIT0

//Handle bidirectionality of PGD
#define DIR_PGD_RD P5DIR&=~PGD
#define DIR_PGD_WR P5DIR|=PGD

#define SET_MCLR P5OUT|=MCLR
#define CLR_MCLR P5OUT&=~MCLR
#define SET_PGD P5OUT|=PGD
#define CLR_PGD P5OUT&=~PGD
#define SET_PGC P5OUT|=PGC
#define CLR_PGC P5OUT&=~PGC

#define READ_PGD (P5IN&PGD?1:0)


//! Set pins as appropriate for dsPIC33F/PIC24H
void pic33f_setup();

//! Start ICSP with an attached dsPIC33F/PIC24H
void pic33f_connect();

/*! Stop ICSP session; maybe not necessary, but cleaner since a
    minimum delay is required before dropping MCLR pin after last
    transmission to dsPIC33F/PIC24H chip. */
void pic33f_disconnect();

//! ICSP SIX command: execute single command on attached dsPIC33F/PIC24H.
void pic33f_six( unsigned int highb, unsigned int loww );

//! ICSP REGOUT command: read contents of VISI register
unsigned int pic33f_regout();

//! Execute a list of commands on attached dsPIC33F/PIC24H.
void pic33f_sixlist( unsigned int list_len );

//! Execute a list of ICSP commands on attached PIC
void pic33f_cmdlist(unsigned int list_len);

//! Start Enhanced ICSP session with dsPIC33F/PIC24H (assumes Programming Executive is present).
void pic33f_eicsp_connect();

/*! Get Application ID (u8), Device ID (i.e. DEVID; u16) and hardware
    revision (u16). Results are dumped to the host connection (a la
    txdata, app is PIC and verb is PIC_DEVID33F).

    This function assumes no ICSP (or Enhanced ICSP) session is currently open!

	Returns number of bytes written to cmddata buffer.
*/
unsigned int pic33f_getid();

//! Write word
void pic33f_trans16( unsigned int word );

//! Write byte
void pic33f_trans8( unsigned char byte );

 
//Command codes
#define PIC_DEVID33F   0x81 //! Read Device and Application ID
#define PIC_SIX33F     0x82 //! ICSP six command; execute instruction on target.
#define PIC_REGOUT33F  0x83 //! Read out VISI register.
#define PIC_SIXLIST33F 0x86 /* Buffers list of instructions to MSP430,
							   then executes them over ICSP session
							   with target dsPIC33F/PIC24H chip. */
#define PIC_CMDLIST    0x88 /* Similar to PIC_SIXLIST33F, but includes ICSP command */

#define PIC_RESET33F   0x87 // Reset attached dsPIC33F/PIC24H chip.
#define PIC_START33F   0x84 // Start ICSP session
#define PIC_STOP33F    0x85 // Stop ICSP (basically, drop !MCLR pin and pause briefly)

extern app_t const pic_app;

#endif // PIC_H
