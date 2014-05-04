/* -*- mode: c; c-basic-offset: 8; indent-tabs-mode: t -*- */
/*! \file dspic33f.c

  \author Scott Livingston

  \brief dsPIC33F programmer application for the GoodFET. Structure
         and style is somewhat modeled after avr.c

  \date March-May 2010
*/


#include "platform.h"
#include "command.h"

#include "pic.h"

#define CYCLE_DELAY() delay_ticks(10);

//! Handle a PIC command; currently assumes dsPIC33F/PIC24H
void pic_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len );

// define the pic app's app_t
app_t const pic_app = {

	/* app number */
	PIC,

	/* handle fn */
	pic_handle_fn,

	/* name */
	"PIC",

	/* desc */
	"\tThe PIC app adds support for programming/debugging\n"
	"\tdsPIC33F based devices.\n"
};

void pic33f_setup()
{
	// Initialize pins; do NOT begin transaction.
	P5DIR |= PGC|MCLR;
	P5REN &= ~(PGC|PGD|MCLR);
	DIR_PGD_WR; // Initially PGD in write mode

	SET_MCLR;
	CLR_PGC;
	CLR_PGD;

	prep_timer(); // What better time than now?
}


//! Handle a PIC command; currently assumes dsPIC33F/PIC24H
void pic_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len )
{
	unsigned int nb; // Number of bytes
	unsigned int highb, loww; // Used for ICSP commands

	switch (verb) {

	case PIC_DEVID33F:
		nb = pic33f_getid();
		txdata(app,verb,nb);
		break;

	case PIC_SIX33F:
		loww = *cmddata;
		loww |= (*(cmddata+1)) << 8;
		highb = *(cmddata+2);
		pic33f_six( highb, loww );
		txdata(app,verb,0);
		break;

	case PIC_SIXLIST33F:
		pic33f_sixlist( len ); // Reply to host is handled by pic33f_sixlist.
		break;

	case PIC_REGOUT33F:
		loww = pic33f_regout();
		*cmddata = loww & 0xff;
		*(cmddata+1) = loww >> 8;
		txdata(app,verb,2);
		break;

	case PIC_RESET33F:
		CLR_MCLR;
		delay_ms(20);
		SET_MCLR;
		break;

	case PIC_START33F:
		pic33f_connect();
		txdata(app,verb,0);
		break;

	case PIC_STOP33F:
		pic33f_disconnect();
		txdata(app,verb,0);
		break;

	case PIC_CMDLIST:
		pic33f_cmdlist(len); // reply is handled by pic33f_cmdlist
		break;

	default:
		debugstr( "Verb unimplemented in PIC application." );
		txdata(app,NOK,0);
		break;

	}
}

void pic33f_transcmd(unsigned char cmd) {
  int i = 0;
  DIR_PGD_WR;
  CLR_PGC;
  for (i = 0; i < 4; i++) {
    if (cmd & 0x1)
      SET_PGD;
    else
      CLR_PGD;
    CYCLE_DELAY();
    SET_PGC;
    cmd >>= 1;
    CYCLE_DELAY();
    CLR_PGC;
  }
  CLR_PGD;
}

void pic33f_trans8( unsigned char byte )
{
	/* We only twiddle the PGD and PGC lines.
	   MCLR is assumed to be in the correct state. */
	unsigned int i;
	
	DIR_PGD_WR; // Write mode
	for (i = 0; i < 8; i++) {
		if (byte & 0x01) {
			SET_PGD;
		} else {
			CLR_PGD;
		}
		CYCLE_DELAY();
		SET_PGC;
		byte >>= 1;
		CYCLE_DELAY();

		CLR_PGC;
		//CYCLE_DELAY();
	}
	CLR_PGD;
	DIR_PGD_RD; // Read mode
}

void pic33f_trans16( unsigned int word )
{
	pic33f_trans8( word & 0xff );
	pic33f_trans8( word >> 8 );
}


void pic33f_six( unsigned int highb, unsigned int loww )
{
	/* dsPIC33F/PIC24H instructions have width 24 bits, so we use the
	   lower 8 bits of highb and (all 16 bits of) loww to form the
	   instruction.

	   Shift in the instruction.  Note that it does not execute until
	   the next 4 clock cycles (which also corresponds to a command
	   receipt time). */
	pic33f_transcmd(0);
	pic33f_trans16( loww );
	pic33f_trans8( highb );
	DIR_PGD_RD;
}


unsigned int pic33f_regout()
{	
	unsigned int i;
	unsigned int result = 0x0000;

	DIR_PGD_WR;
	
	// Shift in command (REGOUT: 0001b).
	pic33f_transcmd(1);

	// Pump clock for 8 cycles, and switch PGD direction to read.
	for (i = 0; i < 7; i++) {
		SET_PGC;
		CYCLE_DELAY();
		CLR_PGC;
		CYCLE_DELAY();
	}
	DIR_PGD_RD;

	/* Now read VISI register (LSb first, as usual).
       Note that when reading from attached device, data is valid (to
	   be read) on falling clock edges. */
	for (i = 0; i < 16; i++) {
		SET_PGC;
		CYCLE_DELAY();
		CLR_PGC;
		result |= READ_PGD << i;
		CYCLE_DELAY();
	}
#if 1
	/* One last tick apparently is needed here, at least by the
	   dsPIC33FJ128GP708 chip that I am working with. Note that this
	   is not in the flash programming specs. */
	SET_PGC; 
	CYCLE_DELAY();
	CLR_PGC;
	CYCLE_DELAY();
#endif

	return result;
}

void pic33f_cmdlist(unsigned int list_len) {
	/* commands are written as 4-byte little-endian records, where
	   the low 4 bits of first byte contains the command, and the
	   next three bytes contain the data.

	   Currently this only supports the SIX and REGOUT
	   instructions.

	   SIX instructions return no data. REGOUT instructions return
	   the 16-bit value read as two bytes, lower byte first.
	   
	   The final two bytes of the response are the 2's complement
	   inverse of the sum of the response words. i.e., if the
	   response is correctly recieved, the sum of the words should
	   be 0.

	   This is sent when the goodfet is done running the command
	   list, and is ready for further commands.
	*/
	
	unsigned char cmd;
	unsigned int response_word;
	unsigned int checksum = 0;
	int response_count;
	int i;
	list_len &= ~3; // truncate to multiple of 4 bytes.
	if (list_len > CMDDATALEN)
		list_len = CMDDATALEN;
	response_count = 1;
	for (i = 0; i < list_len; i += 4) {
		cmd = cmddata[i];
		if (cmd == 0)
			continue;
		else if (cmd == 1)
			response_count ++;
		else
			goto error;
	}
	txhead(PIC, PIC_CMDLIST, response_count << 1);

	for (i = 0; i < list_len; i+= 4) {
		cmd = cmddata[i];
		if (cmd == 0) {
			// SIX command
			pic33f_transcmd(0);
			pic33f_trans8(cmddata[i+1]);
			pic33f_trans8(cmddata[i+2]);
			pic33f_trans8(cmddata[i+3]);
			
		} else if (cmd == 1) {
			// REGOUT command
			response_word = pic33f_regout();
			checksum += response_word;
			response_count--;
			txword(response_word);
		}
	}
	txword(~checksum + 1);
	if (response_count != 1)
		debugstr("Response count wrong");
	return;
 error:
	txdata(PIC, NOK, 0);
}

/* This should be replaced by pic33f_cmdlist */
void pic33f_sixlist( unsigned int list_len )
{
	unsigned int k;
	unsigned int instr_loww;

	// Bound to Rx buffer size.
	if (list_len > CMDDATALEN)
		list_len = CMDDATALEN;

	// Run each instruction!
	for (k = 0; k < list_len-2; k+=3) {
		instr_loww = *(cmddata+k);
		instr_loww |= (*(cmddata+k+1)) << 8;
		pic33f_six( *(cmddata+k+2), instr_loww );
	}

	// Reply with total number of bytes used from Rx buffer.
	txdata( PIC, PIC_SIXLIST33F, k );
}


/* This is slated to be replaced by pic33f_cmdlist */
unsigned int pic33f_getid()
{
	unsigned int result;
	unsigned int nb = 0;

	pic33f_connect();

	// Read application ID.
	pic33f_six( 0x04, 0x0200 ); // goto 0x200 (i.e. reset)
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x20, 0x0800 ); // mov #0x80, W0
	pic33f_six( 0x88, 0x0190 ); // mov W0, TBLPAG
	pic33f_six( 0x20, 0x7F00 ); // mov #0x7F0, W0
	pic33f_six( 0x20, 0x7841 ); // mov #VISI, W1
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0xBA, 0x0890 ); // TBLRDL [W0], [W1]
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x00, 0x0000 ); // nop
	result = pic33f_regout();
	*cmddata = result & 0xff;
	nb += 1;

	// Read DEVID.
	pic33f_six( 0x20, 0x0FF0 ); // mov #0xFF, W0
	pic33f_six( 0x88, 0x0190 ); // mov W0, TBLPAG
	pic33f_six( 0xEB, 0x0000 ); // clr W0
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0xBA, 0x08B0 ); // TBLRDL [W0++], [W1]
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x00, 0x0000 ); // nop
	result = pic33f_regout();
	*(cmddata+1) = result & 0xff;
	*(cmddata+2) = result >> 8;
	nb += 2;

	// Read hardware revision.
	pic33f_six( 0xBA, 0x0890 ); // TBLRDL [W0++], [W1]
	pic33f_six( 0x00, 0x0000 ); // nop
	pic33f_six( 0x00, 0x0000 ); // nop
	result = pic33f_regout();
	*(cmddata+3) = result & 0xff;
	*(cmddata+4) = result >> 8;
	nb += 2;

	pic33f_disconnect();

	return nb;
}


void pic33f_connect()
{
	unsigned int key_low;
	unsigned int key_high;

	key_low = ICSP_KEY_LOW;
	key_high = ICSP_KEY_HIGH;

	pic33f_setup();

	CLR_PGC;
	delay_us(1);
	
	CLR_MCLR;
	delay_ms(3);
	SET_MCLR;
	delay_us(200);
	CLR_MCLR;
	delay_us(10);
	
	// Enter ICSP key
	pic33f_trans8( key_low & 0xff );
	key_low = key_low >> 8;
	pic33f_trans8( key_low & 0xff );
	pic33f_trans8( key_high & 0xff );
	key_high = key_high >> 8;
	pic33f_trans8( key_high & 0xff );

	delay_us(1);
	SET_MCLR; // ...and pull MCLR pin back up.
	delay_ms(25); // Now wait about 25 ms (required per spec!).

	/* The first ICSP command must be a SIX, and further, 9 bits are
       required before the instruction (to be executed), rather than
       the typical 4 bits. Thus, to simplify code, I simply load a nop
       here; hence 33 bits are shifted into the dsPIC33F/PIC24H. */
	DIR_PGD_WR;
	CLR_PGD;
	CLR_PGC;
	for (key_low = 0; key_low < 33; key_low++) {
		SET_PGC;
		CYCLE_DELAY();
		CLR_PGC;
		CYCLE_DELAY();
	}
	DIR_PGD_RD;

}


void pic33f_disconnect()
{
	DIR_PGD_WR;
	CLR_PGD;
	CLR_PGC;
	delay_ms(10);
	CLR_MCLR;
}
