/*! \file sbw.c
  \author Travis Goodspeed and Mark Rages
  \brief Spy-Bi-Wire Mod of JTAG430 and JTAG430X
  
  As SBW is merely a multiplexed method of handling JTAG signals, this
  module works by replacing preprocessor definitions in the
  traditional modules to make them SBW compatible.  Function pointers
  would be size efficient, but so it goes.
*/

#include "platform.h"
#include "command.h"
//#include "jtag.h"
#include "jtag430.h"

#define SBWREWRITE
#include "sbw.h"

// define the sbw app's app_t
app_t const sbw_app = {
  /* app number */
  SBW,
  
  /* handle fn */
  sbw_handler_fn,
  
  /* name */
  "SBW",
  
  /* desc */
  "\tThe SBW app adds to the basic JTAG app\n"
  "\tsupport for SBW'ing MSP430 devices with two wires.\n"
};

int sbw_tms=1, sbw_tdi=1, sbw_tdo=0;

void sbw_clock() {
  //exchange TMS
  SETSBWIO(sbw_tms);
  SBWCLK();

  //exchange TDI
  SETSBWIO(sbw_tdi);
  SBWCLK();

  //exchange TDO
  P5DIR &= ~SBWTDIO; //input mode
  P5OUT &= ~SBWTCK;  //Drop Metaclock
  sbw_tdo=!!(P5IN & SBWTDIO);
  P5OUT |= SBWTCK;   //output mode
  P5DIR |= SBWTDIO;  //Raise Metaclock

  //TCK implied
}


//! Shift 8 bits in and out.
unsigned char sbwtrans8(unsigned char byte){
  unsigned int bit;
  SAVETCLK;
  for (bit = 0; bit < 8; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (byte & 0x80)
      {SETMOSI;}
    else
      {CLRMOSI;}
    byte <<= 1;
    
    if(bit==7)
      SETTMS;//TMS high on last bit to exit.
    
    TCKTOCK;
     /* read MISO on trailing edge */
    byte |= READMISO;
  }
  RESTORETCLK;
  
  // update state
  CLRTMS;
  TCKTOCK;
  
  return byte;
}

//! Shift n bits in and out.
unsigned long sbwtransn(unsigned long word,
			 unsigned int bitcount){
  unsigned int bit;
  //0x8000
  unsigned long high=0x8000;
  
  if(bitcount==20)
    high=0x80000;
  if(bitcount==16)
    high= 0x8000;
  
  SAVETCLK;
  
  for (bit = 0; bit < bitcount; bit++) {
    /* write MOSI on trailing edge of previous clock */
    if (word & high)
      {SETMOSI;}
    else
      {CLRMOSI;}
    word <<= 1;
    
    if(bit==bitcount-1)
      SETTMS;//TMS high on last bit to exit.
    
    TCKTOCK;
    /* read MISO on trailing edge */
    word |= READMISO;
  }
  
  if(bitcount==20){
    word = ((word << 16) | (word >> 4)) & 0x000FFFFF;
  }
  
  RESTORETCLK;
  
  // update state
  CLRTMS;
  TCKTOCK;
  
  return word;
}



//! Shift all bits of the DR.
u32 sbw_dr_shift20(unsigned long in){
  // idle
  SETTMS;
  TCKTOCK;
  // select DR
  CLRTMS;
  TCKTOCK;
  // capture IR
  TCKTOCK;
  
  // shift DR, then idle
  return(sbwtransn(in,20));
}


//! Shift 16 bits of the DR.
u16 sbw_dr_shift16(unsigned int in){
  // idle
  SETTMS; // 1
  TCKTOCK;
  // select DR
  CLRTMS; // 0
  TCKTOCK;
  // capture IR
  TCKTOCK;
  
  // shift DR, then idle
  return(sbwtransn(in,16));
}


//! Shift 8 bits of the IR.
u8 sbw_ir_shift8(unsigned char in){
  // idle
  SETTMS;
  TCKTOCK;
  // select DR
  TCKTOCK;
  // select IR
  CLRTMS;
  TCKTOCK;
  // capture IR
  TCKTOCK;
  
  // shift IR, then idle.
  return(sbwtrans8(in));
}


void sbwSETTCLK(){
  SETSBWIO(sbw_tms);
  SBWCLK();

  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 

  SBWCLK();
  
  P5DIR &= ~SBWTDIO;
  P5OUT &= ~SBWTCK; 
  //tdo=!!(P5IN & SBWTDIO);
  P5OUT |= SBWTCK;
  P5DIR |= SBWTDIO; 
}

void sbwCLRTCLK(){
  SETSBWIO(sbw_tms);
  SBWCLK();

  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 
  SETSBWIO(1);asm("nop");asm("nop");	 
  SETSBWIO(0);asm("nop");asm("nop");	 

  SBWCLK();

  P5DIR &= ~SBWTDIO;
  P5OUT &= ~SBWTCK; 
  //tdo=!!(P5IN & SBWTDIO);
  P5OUT |= SBWTCK;
  P5DIR |= SBWTDIO;   
}




//! Set the program counter.
void sbw430_setpc(unsigned int adr){
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x3401);// release low byte
  sbw_ir_shift8(IR_DATA_16BIT);
  sbw_dr_shift16(0x4030);//Instruction to load PC
  CLRTCLK;
  SETTCLK;
  sbw_dr_shift16(adr);// Value for PC
  CLRTCLK;
  sbw_ir_shift8(IR_ADDR_CAPTURE);
  SETTCLK;
  CLRTCLK ;// Now PC is set to "PC_Value"
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2401);// low byte controlled by SBW
}

//! Halt the CPU
void sbw430_haltcpu(){
  //sbw430_setinstrfetch();
  
  sbw_ir_shift8(IR_DATA_16BIT);
  sbw_dr_shift16(0x3FFF);//JMP $+0
  
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2409);//set SBW_HALT bit
  SETTCLK;
}

//! Release the CPU
void sbw430_releasecpu(){
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2401);
  sbw_ir_shift8(IR_ADDR_CAPTURE);
  SETTCLK;
}

//! Read data from address
unsigned int sbw430_readmem(unsigned int adr){
  unsigned int toret;
  sbw430_haltcpu();
  
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  
  if(adr>0xFF)
    sbw_dr_shift16(0x2409);//word read
  else
    sbw_dr_shift16(0x2419);//byte read
  sbw_ir_shift8(IR_ADDR_16BIT);
  sbw_dr_shift16(adr);//address
  sbw_ir_shift8(IR_DATA_TO_ADDR);
  SETTCLK;

  CLRTCLK;
  toret=sbw_dr_shift16(0x0000);//16 bit return
  
  return toret;
}

//! Write data to address.
void sbw430_writemem(unsigned int adr, unsigned int data){
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  if(adr>0xFF)
    sbw_dr_shift16(0x2408);//word write
  else
    sbw_dr_shift16(0x2418);//byte write
  sbw_ir_shift8(IR_ADDR_16BIT);
  sbw_dr_shift16(adr);
  sbw_ir_shift8(IR_DATA_TO_ADDR);
  sbw_dr_shift16(data);
  SETTCLK;
}

//! Write data to flash memory.  Must be preconfigured.
void sbw430_writeflashword(unsigned int adr, unsigned int data){
  
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2408);//word write
  sbw_ir_shift8(IR_ADDR_16BIT);
  sbw_dr_shift16(adr);
  sbw_ir_shift8(IR_DATA_TO_ADDR);
  sbw_dr_shift16(data);
  SETTCLK;
  
  //Return to read mode.
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2409);
  
  /*
  sbw430_writemem(adr,data);
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2409);
  */
  
  debugstr("ERROR: Haven't got ASM to flash-pulse SBW.");
  
  //Pulse TCLK
  //sbw430_tclk_flashpulses(35); //35 standard
}

//! Configure flash, then write a word.
void sbw430_writeflash(unsigned int adr, unsigned int data){
  sbw430_haltcpu();
  
  //FCTL1=0xA540, enabling flash write
  sbw430_writemem(0x0128, 0xA540);
  //FCTL2=0xA540, selecting MCLK as source, DIV=1
  sbw430_writemem(0x012A, 0xA540);
  //FCTL3=0xA500, should be 0xA540 for Info Seg A on 2xx chips.
  sbw430_writemem(0x012C, 0xA500); //all but info flash.
  
  //Write the word itself.
  sbw430_writeflashword(adr,data);
  
  //FCTL1=0xA500, disabling flash write
  sbw430_writemem(0x0128, 0xA500);
  
  //sbw430_releasecpu();
}



//! Power-On Reset
void sbw430_por(){
  unsigned int sbwid;

  // Perform Reset
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2C01); // apply
  sbw_dr_shift16(0x2401); // remove
  CLRTCLK;
  SETTCLK;
  CLRTCLK;
  SETTCLK;
  CLRTCLK;
  sbwid = sbw_ir_shift8(IR_ADDR_CAPTURE); // get SBW identifier
  SETTCLK;
  
  sbw430_writemem(0x0120, 0x5A80);   // Diabled Watchdog
}



#define ERASE_GLOB 0xA50E
#define ERASE_ALLMAIN 0xA50C
#define ERASE_MASS 0xA506
#define ERASE_MAIN 0xA504
#define ERASE_SGMT 0xA502

//! Configure flash, then write a word.
void sbw430_eraseflash(unsigned int mode, unsigned int adr, unsigned int count){
  sbw430_haltcpu();
  
  //FCTL1= erase mode
  sbw430_writemem(0x0128, mode);
  //FCTL2=0xA540, selecting MCLK as source, DIV=1
  sbw430_writemem(0x012A, 0xA540);
  //FCTL3=0xA500, should be 0xA540 for Info Seg A on 2xx chips.
  sbw430_writemem(0x012C, 0xA500);
  
  //Write the erase word.
  sbw430_writemem(adr, 0x55AA);
  //Return to read mode.
  CLRTCLK;
  sbw_ir_shift8(IR_CNTRL_SIG_16BIT);
  sbw_dr_shift16(0x2409);
  
  //Send the pulses.
  debugstr("ERROR: Haven't got ASM to flash-pulse SBW.");
  //sbw430_tclk_flashpulses(count);
  
  //FCTL1=0xA500, disabling flash write
  sbw430_writemem(0x0128, 0xA500);
  
  //sbw430_releasecpu();
}


//! Reset the TAP state machine.
void sbw430_resettap(){
  int i;
  // Settle output
  SETTDI; //430X2
  SETTMS;
  //SETTDI; //classic
  TCKTOCK;

  // Navigate to reset state.
  // Should be at least six.
  for(i=0;i<4;i++){
    TCKTOCK;
  }

  // test-logic-reset
  CLRTMS;
  TCKTOCK;

  SETTMS;
  // idle

    
  /* sacred, by spec.
     Sometimes this isn't necessary.  */
  // fuse check
  CLRTMS;
  delay(50);
  SETTMS;
  CLRTMS;
  delay(50);
  SETTMS;
  /**/
  
}

void sbwsetup(){

  /* To select the 2-wire SBW mode, the SBWTDIO line is held high and
     the first clock is applied on SBWTCK. After this clock, the
     normal SBW timings are applied starting with the TMS slot, and
     the normal JTAG patterns can be applied, typically starting with
     the Tap Reset and Fuse Check sequence.  The SBW mode is exited by
     holding the TEST/SWBCLK low for more than 100 μs. 
  */

  // tdio up, tck low
  //   
  P5OUT &= ~SBWTCK;
  P5OUT |= SBWTDIO;
  P5DIR |= SBWTDIO|SBWTCK;

  msdelay(5);
  SBWCLK();

  SBWCLK();

  // now we're in SBW mode
}


//! Start SBW, take pins
void sbw430_start(){
  sbwsetup();
  
  //Known-good starting position.
  //Might be unnecessary.
  SETTST;
  SETRST;
  delay(0xFFFF);
  
  sbwsetup();

  //Perform a reset and disable watchdog.
  sbw430_por();
  sbw430_writemem(0x120,0x5a80);//disable watchdog
  sbw430_haltcpu();
}

//! Start normally, not SBW.
void sbw430_stop(){
  debugstr("Exiting SBW.");
  sbwsetup();
  
  //Known-good starting position.
  //Might be unnecessary.
  //SETTST;
  CLRTST;
  SETRST;
  delay(0xFFFF);
  
  //Entry sequence from Page 67 of SLAU265A for 4-wire MSP430 SBW
  CLRRST;
  delay(0xFFFF);
  SETRST;
  //P5DIR&=~RST;
  //delay(0xFFFF);
  
}

//! Set CPU to Instruction Fetch
void sbw430_setinstrfetch(){
  
  sbw_ir_shift8(IR_CNTRL_SIG_CAPTURE);

  // Wait until instruction fetch state.
  while(1){
    if (sbw_dr_shift16(0x0000) & 0x0080)
      return;
    CLRTCLK;
    SETTCLK;
  }
}


//! Stop JTAG, release pins
void sbw_stop(){
  P5OUT=0;
  P4OUT=0;
}



//! Handles classic MSP430 SBW commands.  Forwards others to SBW.

void sbw_handler_fn(u8 app, u8 verb, u32 len){
  unsigned long at;
  unsigned int i, val;
  
  
  /* FIXME
   * Sometimes SBW doesn't init correctly.
   * This restarts the connection if the masked-rom
   * chip ID cannot be read.  Should print warning
   * for testing server.
   */
  while((i=sbw430_readmem(0xff0))==0xFFFF){
    debugstr("start");
    sbw430_start();
    P1OUT^=1;
  }
  P1OUT&=~1;
  

  //debughex(verb);
  switch(verb){
  case SETUP:
    sbwsetup();
    txdata(app,verb,0);
    break;
  case START:
    //Enter SBW mode.
    sbw430_start();
    //TAP setup, fuse check
    sbw430_resettap();
    
    cmddata[0]=sbw_ir_shift8(IR_BYPASS);    
    //cmddata[0]=0x89; //STINT
    txdata(app,verb,1);
    break;
  case STOP:
    sbw430_stop();
    txdata(app,verb,0);
    break;
  case JTAG430_HALTCPU:
    sbw430_haltcpu();
    txdata(app,verb,0);
    break;
  case JTAG430_RELEASECPU:
    sbw430_releasecpu();
    txdata(app,verb,0);
    break;
  case JTAG430_SETINSTRFETCH:
    sbw430_setinstrfetch();
    txdata(app,verb,0);
    break;
    
  case JTAG430_READMEM:
  case PEEK:
    at=cmddatalong[0];
    
    //Fetch large blocks for bulk fetches,
    //small blocks for individual peeks.
    if(len>5)
      len=(cmddataword[2]);//always even.
    else
      len=2;
    len&=~1;//clear lsbit
    
    txhead(app,verb,len);
    for(i=0;i<len;i+=2){
      sbw430_resettap();
      val=sbw430_readmem(at);
      
      at+=2;
      serial_tx(val&0xFF);
      serial_tx((val&0xFF00)>>8);
    }
    break;
  case JTAG430_WRITEMEM:
  case POKE:
    sbw430_haltcpu();
    sbw430_writemem(cmddataword[0],cmddataword[2]);
    cmddataword[0]=sbw430_readmem(cmddataword[0]);
    txdata(app,verb,2);
    break;

  case JTAG430_WRITEFLASH:
    at=cmddataword[0];
    
    for(i=0;i<(len>>1)-2;i++){
      //debugstr("Poking flash memory.");
      sbw430_writeflash(at+(i<<1),cmddataword[i+2]);
      //Reflash if needed.  Try this twice to save grace?
      if(cmddataword[i]!=sbw430_readmem(at))
	sbw430_writeflash(at+(i<<1),cmddataword[i+2]);
    }
    
    //Return result of first write as a word.
    cmddataword[0]=sbw430_readmem(cmddataword[0]);
    
    txdata(app,verb,2);
    break;
  case JTAG430_ERASEFLASH:
    sbw430_eraseflash(ERASE_MASS,0xFFFE,0x3000);
    txdata(app,verb,0);
    break;
  case JTAG430_SETPC:
    sbw430_haltcpu();
    sbw430_setpc(cmddataword[0]);
    sbw430_releasecpu();
    txdata(app,verb,0);
    break;
    
  case JTAG430_COREIP_ID:
  case JTAG430_DEVICE_ID:
    cmddataword[0]=0;
    cmddataword[1]=0;
    txdata(app,verb,4);
    break;
    
  default:
    //sbwhandle(app,verb,len);
    debugstr("ERROR, classic JTAG instruction in SBW.");
    txdata(app,verb,4);
  }
  //sbw430_resettap();  //DO NOT UNCOMMENT
}
