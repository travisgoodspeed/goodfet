/*! \file chipcon.c
  \author Travis Goodspeed
  \brief Chipcon 8051 debugging.
*/


//This is like SPI, except that you read or write, not both.

/* N.B. The READ verb performs a write of all (any) supplied data,
   then reads a single byte reply from the target.  The WRITE verb
   only writes.
*/

#include "platform.h"
#include "command.h"
#include "chipcon.h"

//! Handles a chipcon command.
void cc_handle_fn( uint8_t const app,
				   uint8_t const verb,
				   uint32_t const len);

// define the jtag app's app_t
app_t const chipcon_app = {

	/* app number */
	CHIPCON,

	/* handle fn */
	cc_handle_fn,

	/* name */
	"CHIPCON",

	/* desc */
	"\tThe CHIPCON app adds support for debugging the chipcon\n"
	"\t8051 processor.\n"
};

/* Concerning clock rates, the maximimum clock rates are defined on
   page 4 of the spec.  They vary, but are roughly 30MHz.  Raising
   this clock rate might allow for clock glitching, but the GoodFET
   isn't sufficient fast for that.  Perhaps a 200MHz ARM or an FPGA in
   the BadassFET?
*/

//Pins and I/O
//MISO and MOSI are the same pin, direction changes.

#if (platform == tilaunchpad)
/*
 * The Launchpad has only pins easily available
 * P5.3 TCK	SCK		(labeled TEST J3-10 J2-17)	DC closest to antenna		(blue)
 * P5.2 IO	MISO MOSI	(labeled RST  J3-8  J2-16)	DD next to closer to USB		(yellow)
 * P3.6 txd1	RST		(labeled RXD  J3-6  J1-4)	next to GND, which is closest to USB	(orange)
 * P3.7 rxd1	RST		(labeled TXD  J3-4  J1-3) 	connect to led1 J1-2
 *
 * for a permanent marriage between a TI-Launchpad, move RST to pin48 P5.4
 * (requeries soldering) and use rxd/txd for direct communication with IM-ME dongle.
 */

#define RST  BIT6	// P3.7
#include <msp430_serial.h>


//Normal pins.
#else  
#define RST  BIT0       // P5.0
#define dputs(s)
#endif

#define MOSI BIT2
#define MISO BIT2
#define SCK  BIT3


//This could be more accurate.
//Does it ever need to be?
#define CCSPEED 3
//#define CCSPEED 3
//#define CCDELAY(x) delay_ms(x)
#define CCDELAY(x)

#define SETMOSI SPIOUT|=MOSI
#define CLRMOSI SPIOUT&=~MOSI
#define SETCLK SPIOUT|=SCK
#define CLRCLK SPIOUT&=~SCK
#define READMISO (SPIIN&MISO?1:0)

#if (platform == tilaunchpad)
#  if (SPIDIR != P5DIR)
#    error "SPIDIR != P5DIR"
#  endif
#  if (SPIOUT != P5OUT)
#    error "SPIOUT != P5OUT"
#  endif
#  define SETRST  P3OUT|=RST
#  define CLRRST  P3OUT&=~RST
#else
#  define SETRST  P5OUT|=RST
#  define CLRRST  P5OUT&=~RST
#endif

#define CCWRITE SPIDIR|=MOSI
#define CCREAD SPIDIR&=~MISO

//! Set up the pins for CC mode.  Does not init debugger.
void ccsetup(){
#if (platform == tilaunchpad)
	dputs("ccsetup");
  SPIOUT|=MOSI+SCK;
  SPIDIR|=MOSI+SCK;
  P3OUT|=RST;
  P3DIR|=RST;
	dputs("done ccsetup");
#else
  SPIOUT|=MOSI+SCK+RST;
  SPIDIR|=MOSI+SCK+RST;
#endif
  //P5REN=0xFF;
}


/* 33 cycle critical region
0000000e <ccdebuginit>:
   e:	f2 d0 0d 00 	bis.b	#13,	&0x0031	;5 cycles
  12:	31 00
  14:	f2 c2 31 00 	bic.b	#8,	&0x0031	;4 cycles
  18:	d2 c3 31 00 	bic.b	#1,	&0x0031	;4
  1c:	f2 e2 31 00 	xor.b	#8,	&0x0031	;4
  20:	f2 e2 31 00 	xor.b	#8,	&0x0031	;4
  24:	f2 e2 31 00 	xor.b	#8,	&0x0031	;4
  28:	f2 e2 31 00 	xor.b	#8,	&0x0031	;4
  2c:	d2 d3 31 00 	bis.b	#1,	&0x0031	;4
  30:	30 41       	ret
*/


//! Initialize the debugger
void ccdebuginit(){
  //Port output BUT NOT DIRECTION is set at start.
#if (platform == tilaunchpad)
  dputs("ccdebuginit");
  SPIOUT|=MOSI+SCK;
  P3OUT|=RST;
#else
  SPIOUT|=MOSI+SCK+RST;
#endif

  delay(30); //So the beginning is ready for glitching.

  //Two positive debug clock pulses while !RST is low.
  //Take RST low, pulse twice, then high.
  SPIOUT&=~SCK;
  delay(10);
  CLRRST;

  delay(10);

  //Two rising edges.
  SPIOUT^=SCK; //up
  delay(1);
  SPIOUT^=SCK; //down
  delay(1);
  SPIOUT^=SCK; //up
  delay(1);
  SPIOUT^=SCK; //Unnecessary.
  delay(1);
  //delay(0);

  //Raise !RST.
  SETRST;
}

//! Read and write a CC bit.
unsigned char cctrans8(unsigned char byte){
  unsigned int bit;
  //This function came from the SPI Wikipedia article.
  //Minor alterations.

  for (bit = 0; bit < 8; bit++) {
    CCDELAY(CCSPEED>>2);
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      SETMOSI;
    else
      CLRMOSI;
    byte <<= 1;

    /* half a clock cycle before leading/rising edge */
    CCDELAY(CCSPEED>>2);
    SETCLK;

    /* half a clock cycle before trailing/falling edge */
    CCDELAY(CCSPEED>>2);

    /* read MISO on trailing edge */
    byte |= READMISO;
    CLRCLK;
  }

  return byte;
}

//! Send a command from txbytes.
void cccmd(unsigned char len){
  unsigned char i;
  CCWRITE;
  for(i=0;i<len;i++)
    cctrans8(cmddata[i]);
}

//! Fetch a reply, usually 1 byte.
void ccread(unsigned char len){
  unsigned char i;
  CCREAD;
  for(i=0;i<len;i++)
    cmddata[i]=cctrans8(0);
}

//! Handles a chipcon command.
void cc_handle_fn( uint8_t const app,
				   uint8_t const verb,
				   uint32_t const len)
{
  //Always init.  Might help with buggy lines.
  //Might hurt too.
  //ccdebuginit();
  long i;
  int blocklen, blockadr;

  switch(verb){
    //CC_PEEK and CC_POKE will come later.
  case PEEK:
    cmddata[0]=cc_peekirambyte(cmddata[0]);
    txdata(app,verb,1);
    break;
  case POKE:
    cmddata[0]=cc_pokeirambyte(cmddata[0],cmddata[1]);
    txdata(app,verb,0);
    break;
  case READ:  //Write a command and return 1-byte reply.
    cccmd(len);
    if(cmddata[0]&0x4)
      ccread(1);
    txdata(app,verb,1);
    break;
  case WRITE: //Write a command with no reply.
    cccmd(len);
    txdata(app,verb,0);
    break;
  case START://enter debugger
    ccdebuginit();
    txdata(app,verb,0);
    break;
  case STOP://exit debugger
    //Take RST low, then high.
    CLRRST;
    CCDELAY(CCSPEED);
    SETRST;
    txdata(app,verb,0);
    break;
  case SETUP:
    ccsetup();
    txdata(app,verb,0);
    break;

  //Micro commands!
  case CC_CHIP_ERASE:
  case CC_MASS_ERASE_FLASH:
    cc_chip_erase();
    txdata(app,verb,1);
    break;
  case CC_WR_CONFIG:
    cc_wr_config(cmddata[0]);
    txdata(app,verb,1);
    break;
  case CC_RD_CONFIG:
    cc_rd_config();
    txdata(app,verb,1);
    break;
  case CC_GET_PC:
    cc_get_pc();
    txdata(app,verb,2);
    break;
  case CC_LOCKCHIP:
    cc_lockchip();
    //no break, return status
  case CC_READ_STATUS:
    cc_read_status();
    txdata(app,verb,1);
    break;
  case CC_SET_HW_BRKPNT:
    cc_set_hw_brkpnt(cmddataword[0]);
    txdata(app,verb,1);
    break;
  case CC_HALT:
    cc_halt();
    txdata(app,verb,1);
    break;
  case CC_RESUME:
    cc_resume();
    txdata(app,verb,1);
    break;
  case CC_DEBUG_INSTR:
    cc_debug_instr(len);
    txdata(app,verb,1);
    break;
  case CC_STEP_INSTR:
    cc_step_instr();
    txdata(app,verb,1);
    break;
  case CC_STEP_REPLACE:
    txdata(app,NOK,0);//Don't add this; it's non-standard.
    break;
  case CC_GET_CHIP_ID:
    cmddataword[0]=cc_get_chip_id();
    txdata(app,verb,2);
    break;


  //Macro commands
  case CC_READ_CODE_MEMORY:
    cmddata[0]=cc_peekcodebyte(cmddataword[0]);
    txdata(app,verb,1);
    break;
  case CC_READ_XDATA_MEMORY:
    //Read the length.
    blocklen=1;
    if(len>2)
      blocklen=cmddataword[1];
    blockadr=cmddataword[0];

    //Return that many bytes.
    for(i=0;i<blocklen;i++)
      cmddata[i]=cc_peekdatabyte(blockadr+i);
    txdata(app,verb,blocklen);
    break;

  case CC_WRITE_XDATA_MEMORY:
    cmddata[0]=cc_pokedatabyte(cmddataword[0], cmddata[2]);
    txdata(app,verb,1);
    break;
  case CC_SET_PC:
    cc_set_pc(cmddatalong[0]);
    txdata(app,verb,0);
    break;
  case CC_WRITE_FLASH_PAGE:
    cc_write_flash_page(cmddatalong[0]);
    txdata(app,verb,0);
    break;
  case CC_WIPEFLASHBUFFER:
    for(i=0xf000;i<0xf800;i++)
      cc_pokedatabyte(i,0xFF);
    txdata(app,verb,0);
    break;

  case CC_CLOCK_INIT:
  case CC_PROGRAM_FLASH:
  default:
    debugstr("This Chipcon command is not yet implemented.");
    txdata(app,NOK,0);//TODO implement me.
    break;
  }
}

//! Set the Chipcon's Program Counter
void cc_set_pc(u32 adr){
  cmddata[0]=0x02;             //SetPC
  cmddata[1]=((adr>>8)&0xff);  //HIBYTE
  cmddata[2]=adr&0xff;         //LOBYTE
  cc_debug_instr(3);
  return;
}

//! Erase all of a Chipcon's memory.
void cc_chip_erase(){
  cmddata[0]=CCCMD_CHIP_ERASE; //0x14
  cccmd(1);
  ccread(1);
}
//! Write the configuration byte.
void cc_wr_config(unsigned char config){
  cmddata[0]=CCCMD_WR_CONFIG; //0x1D
  cmddata[1]=config;
  cccmd(2);
  ccread(1);
}

//! Locks the chip.
void cc_lockchip(){
  register int i;

  //debugstr("Locking chip.");
  cc_wr_config(1);//Select Info Flash
  if(!(cc_rd_config()&1))
    debugstr("Config forgotten!");

  //Clear config page.
  for(i=0;i<2048;i++)
    cc_pokedatabyte(0xf000+i,0);
  cc_write_flash_page(0);
  if(cc_peekcodebyte(0))
    debugstr("Failed to clear info flash byte.");

  cc_wr_config(0);
  if(cc_rd_config()&1)
    debugstr("Stuck in info flash mode!");
}

//! Read the configuration byte.
unsigned char cc_rd_config(){
  cmddata[0]=CCCMD_RD_CONFIG; //0x24
  cccmd(1);
  ccread(1);
  return cmddata[0];
}


//! Read the status register
unsigned char cc_read_status(){
  cmddata[0]=CCCMD_READ_STATUS; //0x3f
  cccmd(1);
  ccread(1);
  return cmddata[0];
}

//! Read the CHIP ID bytes.
unsigned short cc_get_chip_id(){
  cmddata[0]=CCCMD_GET_CHIP_ID; //0x68
  cccmd(1);
  ccread(2);


  //Find the flash word size.
  switch(cmddata[0]){
  case 0x01://CC1110
  case 0x11://CC1111
  case 0x81://CC2510
  case 0x91://CC2511
    //debugstr("2 bytes/flash word");
    flash_word_size=0x02;
    break;
  default:
    //debugstr("Warning: Guessing flash word size.");
    //flash_word_size=0;
    break;
  case 0x85://CC2430
  case 0x89://CC2431
    //debugstr("4 bytes/flash word");
    flash_word_size=0x04;
    break;
  }

  //Return the word.
  return cmddataword[0];
}

//! Populates flash buffer in xdata.
void cc_write_flash_buffer(u8 *data, u16 len){
  cc_write_xdata(0xf000, data, len);
}
//! Populates flash buffer in xdata.
void cc_write_xdata(u16 adr, u8 *data, u16 len){
  u16 i;
  for(i=0; i<len; i++){
    cc_pokedatabyte(adr+i,
		    data[i]);
  }
}


//32-bit words, 2KB pages
//0x20 0x00 for CC2430, CC1110
#define HIBYTE_WORDS_PER_FLASH_PAGE 0x02
#define LOBYTE_WORDS_PER_FLASH_PAGE 0x00

/** Ugh, this varies by chip.
    0x800 for CC2430
    0x400 for CC1110
*/
//#define FLASHPAGE_SIZE 0x400
#define MAXFLASHPAGE_SIZE 0x800
#define MINFLASHPAGE_SIZE 0x400


//32 bit words on CC2430
//16 bit words on CC1110
//#define FLASH_WORD_SIZE 0x2
u8 flash_word_size = 0; //0x02;


/* Flash Write Timing
   MHZ | FWT (0xAB)
   12  | 0x10
   13  | 0x11
   16  | 0x15
   24  | 0x20
   26  | 0x23  (IM ME)
   32  | 0x2A  (Modula.si)
*/
//#define FWT 0x23

const u8 flash_routine[] = {
  //0:
  //MOV FADDRH, #imm;
  0x75, 0xAD,
  0x00,//#imm=((address >> 8) / FLASH_WORD_SIZE) & 0x7E,

  //0x75, 0xAB, 0x23, //Set FWT per clock
  0x75, 0xAC, 0x00,                                          //                 MOV FADDRL, #00;
  /* Erase page. */
  0x75, 0xAE, 0x01,                                          //                 MOV FLC, #01H; // ERASE
                                                             //                 ; Wait for flash erase to complete
  0xE5, 0xAE,                                                // eraseWaitLoop:  MOV A, FLC;
  0x20, 0xE7, 0xFB,                                          //                 JB ACC_BUSY, eraseWaitLoop;

  /* End erase page. */
                                                             //                 ; Initialize the data pointer
  0x90, 0xF0, 0x00,                                          //                 MOV DPTR, #0F000H;
                                                             //                 ; Outer loops
  0x7F, HIBYTE_WORDS_PER_FLASH_PAGE,                         //                 MOV R7, #imm;
  0x7E, LOBYTE_WORDS_PER_FLASH_PAGE,                         //                 MOV R6, #imm;
  0x75, 0xAE, 0x02,                                          //                 MOV FLC, #02H; // WRITE
                                                             //                     ; Inner loops
  //24:
  0x7D, 0xde /*FLASH_WORD_SIZE*/,                                     // writeLoop:          MOV R5, #imm;
  0xE0,                                                      // writeWordLoop:          MOVX A, @DPTR;
  0xA3,                                                      //                         INC DPTR;
  0xF5, 0xAF,                                                //                         MOV FWDATA, A;
  0xDD, 0xFA,                                                //                     DJNZ R5, writeWordLoop;
                                                             //                     ; Wait for completion
  0xE5, 0xAE,                                                // writeWaitLoop:      MOV A, FLC;
  0x20, 0xE6, 0xFB,                                          //                     JB ACC_SWBSY, writeWaitLoop;
  0xDE, 0xF1,                                                //                 DJNZ R6, writeLoop;
  0xDF, 0xEF,                                                //                 DJNZ R7, writeLoop;
                                                             //                 ; Done, fake a breakpoint
  0xA5                                                       //                 DB 0xA5;
};


//! Copies flash buffer to flash.
void cc_write_flash_page(u32 adr){
  //Assumes that page has already been written to XDATA 0xF000
  //debugstr("Flashing 2kb at 0xF000 to given adr.");

  if(adr&(MINFLASHPAGE_SIZE-1)){
    debugstr("Flash page address is not on a page boundary.  Aborting.");
    return;
  }

  if(flash_word_size!=2 && flash_word_size!=4){
    debugstr("Flash word size is wrong, aborting write to");
    debughex(adr);
    while(1);
  }

  //Routine comes next
  //WRITE_XDATA_MEMORY(IN: 0xF000 + FLASH_PAGE_SIZE, sizeof(routine), routine);
  cc_write_xdata(0xF000+MAXFLASHPAGE_SIZE,
		 (u8*) flash_routine, sizeof(flash_routine));
  //Patch routine's third byte with
  //((address >> 8) / FLASH_WORD_SIZE) & 0x7E
  cc_pokedatabyte(0xF000+MAXFLASHPAGE_SIZE+2,
		  ((adr>>8)/flash_word_size)&0x7E);
  //Patch routine to define FLASH_WORD_SIZE
  if(flash_routine[25]!=0xde)
    debugstr("Ugly patching code failing in chipcon.c");
  cc_pokedatabyte(0xF000+MAXFLASHPAGE_SIZE+25,
		  flash_word_size);

  //debugstr("Wrote flash routine.");

  //MOV MEMCTR, (bank * 16) + 1;
  cmddata[0]=0x75;
  cmddata[1]=0xc7;
  cmddata[2]=0x51;
  cc_debug_instr(3);
  //debugstr("Loaded bank info.");

  cc_set_pc(0xf000+MAXFLASHPAGE_SIZE);//execute code fragment
  cc_resume();

  //debugstr("Executing.");


  while(!(cc_read_status()&CC_STATUS_CPUHALTED)){
    led_toggle();//blink LED while flashing
  }


  //debugstr("Done flashing.");

  led_off();
}

//! Read the PC
unsigned short cc_get_pc(){
  cmddata[0]=CCCMD_GET_PC; //0x28
  cccmd(1);
  ccread(2);

  //Return the word.
  return cmddataword[0];
}

//! Set a hardware breakpoint.
void cc_set_hw_brkpnt(unsigned short adr){
  debugstr("FIXME: This certainly won't work.");
  cmddataword[0]=adr;
  cccmd(2);
  ccread(1);
  return;
}


//! Halt the CPU.
void cc_halt(){
  cmddata[0]=CCCMD_HALT; //0x44
  cccmd(1);
  ccread(1);
  return;
}
//! Resume the CPU.
void cc_resume(){
  cmddata[0]=CCCMD_RESUME; //0x4C
  cccmd(1);
  ccread(1);
  return;
}


//! Step an instruction
void cc_step_instr(){
  cmddata[0]=CCCMD_STEP_INSTR; //0x5C
  cccmd(1);
  ccread(1);
  return;
}

//! Debug an instruction.
void cc_debug_instr(unsigned char len){
  //Bottom two bits of command indicate length.
  unsigned char cmd=CCCMD_DEBUG_INSTR+(len&0x3); //0x54+len
  CCWRITE;
  cctrans8(cmd);  //Second command code
  cccmd(len&0x3); //Command itself.
  ccread(1);
  return;
}

//! Debug an instruction, for local use.
unsigned char cc_debug(unsigned char len,
	      unsigned char a,
	      unsigned char b,
	      unsigned char c){
  unsigned char cmd=CCCMD_DEBUG_INSTR+(len&0x3);//0x54+len
  CCWRITE;
  cctrans8(cmd);
  if(len>0)
    cctrans8(a);
  if(len>1)
    cctrans8(b);
  if(len>2)
    cctrans8(c);
  CCREAD;
  return cctrans8(0x00);
}

//! Fetch a byte of code memory.
unsigned char cc_peekcodebyte(unsigned long adr){
  /** See page 9 of SWRA124 */
  unsigned char bank=adr>>15,
    lb=adr&0xFF,
    hb=(adr>>8)&0x7F,
    toret=0;
  adr&=0x7FFF;

  //MOV MEMCTR, (bank*16)+1
  cc_debug(3, 0x75, 0xC7, (bank<<4) + 1);
  //MOV DPTR, address
  cc_debug(3, 0x90, hb, lb);

  //for each byte
  //CLR A
  cc_debug(2, 0xE4, 0, 0);
  //MOVC A, @A+DPTR;
  toret=cc_debug(3, 0x93, 0, 0);
  //INC DPTR
  //cc_debug(1, 0xA3, 0, 0);

  return toret;
}


//! Set a byte of data memory.
unsigned char cc_pokedatabyte(unsigned int adr,
			   unsigned char val){
  unsigned char
    hb=(adr&0xFF00)>>8,
    lb=adr&0xFF;

  //MOV DPTR, adr
  cc_debug(3, 0x90, hb, lb);
  //MOV A, val
  cc_debug(2, 0x74, val, 0);
  //MOVX @DPTR, A
  cc_debug(1, 0xF0, 0, 0);

  return 0;
  /*
DEBUG_INSTR(IN: 0x90, HIBYTE(address), LOBYTE(address), OUT: Discard);
for (n = 0; n < count; n++) {
    DEBUG_INSTR(IN: 0x74, inputArray[n], OUT: Discard);
    DEBUG_INSTR(IN: 0xF0, OUT: Discard);
    DEBUG_INSTR(IN: 0xA3, OUT: Discard);
}
   */
}

//! Fetch a byte of data memory.
unsigned char cc_peekdatabyte(unsigned int adr){
  unsigned char
    hb=(adr&0xFF00)>>8,
    lb=adr&0xFF;

  //MOV DPTR, adr
  cc_debug(3, 0x90, hb, lb);
  //MOVX A, @DPTR
  //Must be 2, perhaps for clocking?
  return cc_debug(3, 0xE0, 0, 0);
}


//! Fetch a byte of IRAM.
u8 cc_peekirambyte(u8 adr){
  //CLR A
  cc_debug(2, 0xE4, 0, 0);
  //MOV A, #iram
  return cc_debug(3, 0xE5, adr, 0);
}

//! Write a byte of IRAM.
u8 cc_pokeirambyte(u8 adr, u8 val){
  //CLR A
  cc_debug(2, 0xE4, 0, 0);
  //MOV #iram, #val
  return cc_debug(3, 0x75, adr, val);
  //return cc_debug(3, 0x75, val, adr);
}


