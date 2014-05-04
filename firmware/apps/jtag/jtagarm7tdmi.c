/*! \file jtagarm7tdmi.c
  \brief ARM7TDMI JTAG (AT91R40008, AT91SAM7xxx)
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"
#include "jtagarm7tdmi.h"


/**** 20-pin Connection Information (pin1 is on top-right for both connectors)****
GoodFET  ->  7TDMI 20-pin connector (HE-10 connector)
  1               13 (TDO)
  2               1  (Vdd)
  3               5  (TDI)
  5               7  (TMS)
  7               9  (TCK)
  8               15 (nRST)
  9               4,6,8,10,12,14,16,18,20 (GND)
  11              17/3 (nTRST)  (different sources suggest 17 or 3 alternately)
********************************/

/**** 14-pin Connection Information (pin1 is on top-right for both connectors)****
GoodFET  ->  7TDMI 14-pin connector
  1               11 (TDO)
  2               1  (Vdd)
  3               5  (TDI)
  5               7  (TMS)
  7               9  (TCK)
  8               12 (nRST)
  9               2,4,6,8,10,14 (GND)
  11              3 (nTRST)

http://hri.sourceforge.net/tools/jtag_faq_org.html
********************************/






/****************************************************************
Enabling jtag likely differs with most platforms.  We will attempt to enable most from here.  Override jtagarm7tdmi_start() to extend for other implementations
ARM7TDMI enables three different scan chains:
    * Chain0 - "entire periphery" including data bus
    * Chain1 - core data bus (subset of Chain0)  - Instruction Pipeline
    * Chain2 - EmbeddedICE Logic Registers - This is our way into the fun stuff.
    

---
You can disable EmbeddedICE-RT by setting the DBGEN input LOW.
Caution
Hard wiring the DBGEN input LOW permanently disables all debug functionality.
When DBGEN is LOW, it inhibits DBGDEWPT, DBGIEBKPT, and EDBGRQ to
the core, and DBGACK from the ARM9E-S core is always LOW.
---


---
When the ARM9E-S core is in debug state, you can examine the core and system state
by forcing the load and store multiples into the instruction pipeline.
Before you can examine the core and system state, the debugger must determine
whether the processor entered debug from Thumb state or ARM state, by examining
bit 4 of the EmbeddedICE-RT debug status register. If bit 4 is HIGH, the core has
entered debug from Thumb state.
For more details about determining the core state, see Determining the core and system
state on page B-18.
---


--- olimex - http://www.olimex.com/dev/pdf/arm-jtag.pdf
JTAG signals description:
PIN.1 (VTREF) Target voltage sense. Used to indicate the target’s operating voltage to thedebug tool.
PIN.2 (VTARGET) Target voltage. May be used to supply power to the debug tool.
PIN.3 (nTRST) JTAG TAP reset, this signal should be pulled up to Vcc in target board.
PIN4,6, 8, 10,12,14,16,18,20 Ground. The Gnd-Signal-Gnd-Signal strategy implemented on the 20-way connection scheme improves noiseimmunity on the target connect cable.
*PIN.5 (TDI) JTAG serial data in, should be pulled up to Vcc on target board.
*PIN.7 (TMS) JTAG TAP Mode Select, should be pulled up to Vcc on target board.
*PIN.9 (TCK) JTAG clock.
PIN.11 (RTCK) JTAG retimed clock.Implemented on certain ASIC ARM implementations the host ASIC may need to synchronize external inputs (such as JTAG inputs) with its own internal clock.
*PIN.13 (TDO) JTAG serial data out.
*PIN.15 (nSRST) Target system reset.
*PIN.17 (DBGRQ) Asynchronous debug request.  DBGRQ allows an external signal to force the ARM core into debug mode, should be pull down to GND.
PIN.19 (DBGACK) Debug acknowledge. The ARM core acknowledges debug-mode inresponse to a DBGRQ input.


-----------  SAMPLE TIMES  -----------

TDI and TMS are sampled on the rising edge of TCK and TDO transitions appear on the falling edge of TCK. Therefore, TDI and TMS must be written after the falling edge of TCK and TDO must be read after the rising edge of TCK.

for this module, we keep tck high for all changes/sampling, and then bounce it.
****************************************************************/




// ! Start JTAG, setup pins, reset TAP and return IDCODE
unsigned long jtagarm7tdmi_start() {
  jtagsetup();
  jtagarm7tdmi_resettap();
  return jtagarm7tdmi_idcode();
}


//! Reset TAP State Machine       
void jtagarm7tdmi_resettap(){               // PROVEN
  current_chain = -1;
  jtag_reset_to_runtest_idle();
}



/************************************************************************
* ARM7TDMI core has 6 primary registers to be connected between TDI/TDO
*   * Bypass Register
*   * ID Code Register
*   * Scan Chain Select Register    (4 bits_lsb)
*   * Scan Chain 0                  (105 bits: 32_databits_lsb + ctrlbits + 32_addrbits_msb)
*   * Scan Chain 1                  (33 bits: 32_bits + BREAKPT)
*   * Scan Chain 2                  (38 bits: rw + 5_regbits_msb + 32_databits_msb)
************************************************************************/



/************************** Basic JTAG Verb Commands *******************************/
//! Grab the core ID.
unsigned long jtagarm7tdmi_idcode(){               // PROVEN
  jtagarm7tdmi_resettap();
  jtag_goto_shift_ir();
  jtagtransn(ARM7TDMI_IR_IDCODE, 4, LSB);
  jtag_goto_shift_dr();
  return jtagtransn(0,32, LSB);
}

//!  Connect Bypass Register to TDO/TDI
//unsigned char jtagarm7tdmi_bypass(){               // PROVEN
//  jtagarm7tdmi_resettap();
//  jtag_goto_shift_ir();
//  return jtagarmtransn(ARM7TDMI_IR_BYPASS, 4, LSB, END, NORETIDLE);
//}
//!  INTEST verb - do internal test
//unsigned char jtagarm7tdmi_intest() { 
//  jtag_goto_shift_ir();
//  return jtagarmtransn(ARM7TDMI_IR_INTEST, 4, LSB, END, NORETIDLE); 
//}

//!  EXTEST verb - act like the processor to external components
//unsigned char jtagarm7tdmi_extest() { 
//  jtag_goto_shift_ir();
//  return jtagarmtransn(ARM7TDMI_IR_EXTEST, 4, LSB, END, NORETIDLE);
//}

//!  SAMPLE verb
//unsigned long jtagarm7tdmi_sample() { 
//  jtagarm7tdmi_ir_shift4(ARM7TDMI_IR_SAMPLE);        // ???? same here.
//  return jtagtransn(0,32);
//}

//!  RESTART verb
unsigned long jtagarm7tdmi_restart() { 
  unsigned long retval;
  jtag_goto_shift_ir();
  retval = jtagtransn(ARM7TDMI_IR_RESTART, 4, LSB); 
  current_chain = -1;
  //jtagarm7tdmi_resettap();
  return retval;
}

//!  ARM7TDMI_IR_CLAMP               0x5
//unsigned long jtagarm7tdmi_clamp() { 
//  jtagarm7tdmi_resettap();
//  jtag_goto_shift_ir();
//  jtagarmtransn(ARM7TDMI_IR_CLAMP, 4, LSB, END, NORETIDLE);
//  jtag_goto_shift_dr();
//  return jtagarmtransn(0, 32, LSB, END, RETIDLE);
//}

//!  ARM7TDMI_IR_HIGHZ               0x7
//unsigned char jtagarm7tdmi_highz() { 
//  jtagarm7tdmi_resettap();
//  jtag_goto_shift_ir();
//  return jtagarmtransn(ARM7TDMI_IR_HIGHZ, 4, LSB, END, NORETIDLE);
//}

//! define ARM7TDMI_IR_CLAMPZ              0x9
//unsigned char jtagarm7tdmi_clampz() { 
//  jtagarm7tdmi_resettap();
//  jtag_goto_shift_ir();
//  return jtagarmtransn(ARM7TDMI_IR_CLAMPZ, 4, LSB, END, NORETIDLE);
//}


//!  Connect the appropriate scan chain to TDO/TDI.  SCAN_N, INTEST, ENDS IN SHIFT_DR!!!!!
unsigned long jtagarm7tdmi_scan(int chain, int testmode) {               // PROVEN
/*
When selecting a scan chain the “Run Test/Idle” state should never be reached, other-
wise, when in debug state, the core will not be correctly isolated and intrusive
commands occur. Therefore, it is recommended to pass directly from the “Update”
state” to the “Select DR” state each time the “Update” state is reached.
*/
  unsigned long retval;
  //if (current_chain != chain) {
  //  //debugstr("===change chains===");
    jtag_goto_shift_ir();
    jtagtransn(ARM7TDMI_IR_SCAN_N, 4, LSB | NORETIDLE);
    jtag_goto_shift_dr();
    retval = jtagtransn(chain, 4, LSB | NORETIDLE);
    // put in test mode...
    //jtag_goto_shift_ir();
    //jtagarmtransn(testmode, 4, LSB, END, RETIDLE); 
    current_chain = chain;
  //}    else  {
  //  //debugstr("===NOT change chains===");
  //  retval = current_chain;
  //}
  // put in test mode...
  jtag_goto_shift_ir();
  jtagtransn(testmode, 4, LSB); 
  return(retval);
}


//!  Connect the appropriate scan chain to TDO/TDI.  SCAN_N, INTEST, ENDS IN SHIFT_DR!!!!!
unsigned long jtagarm7tdmi_scan_intest(int chain) {               // PROVEN
  return jtagarm7tdmi_scan(chain, ARM7TDMI_IR_INTEST);
}




//! push an instruction into the pipeline
unsigned long jtagarm7tdmi_instr_primitive(unsigned long instr, char breakpt){  // PROVEN
  unsigned long retval;
  jtagarm7tdmi_scan_intest(1);

  jtag_goto_shift_dr();
  // if the next instruction is to run using MCLK (master clock), set TDI
  if (breakpt)
    {
    SETMOSI;
    count_sysspd_instr_since_debug++;
    } 
  else
    {
    CLRMOSI; 
    count_dbgspd_instr_since_debug++;
    }
  jtag_tcktock();
  
  // Now shift in the 32 bits
  retval = jtagtransn(instr, 32, 0);    // Must return to RUN-TEST/IDLE state for instruction to enter pipeline, and causes debug clock.
  return(retval);
  
}

//! push NOP into the instruction pipeline
unsigned long jtagarm7tdmi_nop(char breakpt){  // PROVEN
  if (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT) 
    return jtagarm7tdmi_instr_primitive(THUMB_INSTR_NOP, breakpt);
  return jtagarm7tdmi_instr_primitive(ARM_INSTR_NOP, breakpt);
}

/*    stolen from ARM DDI0029G documentation, translated using ARM Architecture Reference Manual (14128.pdf)
STR R0, [R0]; Save R0 before use
MOV R0, PC ; Copy PC into R0
STR R0, [R0]; Now save the PC in R0
BX PC ; Jump into ARM state
MOV R8, R8 ;
MOV R8, R8 ;
NOP
NOP

*/

//! set the current mode to ARM, returns PC (FIXME).  Should be used by haltcpu(), which should also store PC and the THUMB state, for use by releasecpu();
unsigned long jtagarm7tdmi_setMode_ARM(unsigned char restart){               // PROVEN  BUT FUGLY! FIXME: clean up and store and replace clobbered r0
  jtagarm7tdmi_resettap();                  // seems necessary for some reason.  ugh.
  unsigned long retval = 0xffL;
  if ((current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT)){
    debugstr("=== Switching to ARM mode ===");
    cmddatalong[1] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_NOP,0);
    cmddatalong[2] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_STR_R0_r0,0);
    cmddatalong[3] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_MOV_R0_PC,0);
    cmddatalong[4] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_STR_R0_r0,restart);
    cmddatalong[5] = jtagarm7tdmi_instr_primitive(THUMB_INSTR_BX_PC,0);
  } else {
    jtagarm7tdmi_set_register(15,(last_halt_pc|0xfffffffc)-24);
    jtagarm7tdmi_nop( restart);
    cmddatalong[1] = jtagarm7tdmi_instr_primitive(ARM_INSTR_B_IMM,0);
  }
  if (restart) {
    jtagarm7tdmi_restart();
  } else {
    jtagarm7tdmi_nop(0);
    jtagarm7tdmi_nop(0);
    jtagarm7tdmi_nop(0);
    jtagarm7tdmi_set_register(0,cmddataword[5]);
  }
  jtagarm7tdmi_resettap();                  // seems necessary for some reason.  ugh.
  current_dbgstate = jtagarm7tdmi_get_dbgstate();
  return(retval);
}


//! set the current mode to ARM, returns PC (FIXME).  Should be used by releasecpu()
unsigned long jtagarm7tdmi_setMode_THUMB(unsigned char restart){               // PROVEN
  jtagarm7tdmi_resettap();                  // seems necessary for some reason.  ugh.
  debugstr("=== Switching to THUMB mode ===");
  unsigned long retval = 0xffL;
  while (!(current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT)&& retval-- > 0){
    last_halt_pc |= 1;
    jtagarm7tdmi_set_register(0, last_halt_pc);
    jtagarm7tdmi_instr_primitive(ARM_INSTR_NOP,restart);
    jtagarm7tdmi_instr_primitive(ARM_INSTR_BX_R0,0);
    if (restart) {
      jtagarm7tdmi_restart();
    } else {
      jtagarm7tdmi_instr_primitive(ARM_INSTR_NOP,0);
      jtagarm7tdmi_instr_primitive(ARM_INSTR_NOP,0);
      jtagarm7tdmi_resettap();                  // seems necessary for some reason.
    }
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
  }
  return(retval);
}




/************************* EmbeddedICE Primitives ****************************/
//! shifter for writing to chain2 (EmbeddedICE). 
unsigned long eice_write(unsigned char reg, unsigned long data){
  unsigned long retval, temp;
  jtagarm7tdmi_scan_intest(2);
  // Now shift in the 32 bits
  jtag_goto_shift_dr();
  retval = jtagtransn(data, 32, LSB| NOEND| NORETIDLE);          // send in the data - 32-bits lsb
  temp = jtagtransn(reg, 5, LSB| NOEND| NORETIDLE);              // send in the register address - 5 bits lsb
  jtagtransn(1, 1, LSB);                           // send in the WRITE bit
  
  return(retval); 
}

//! shifter for reading from chain2 (EmbeddedICE).
unsigned long eice_read(unsigned char reg){               // PROVEN
  unsigned long temp, retval;
  //debugstr("eice_read");
  //debughex(reg);
  jtagarm7tdmi_scan_intest(2);

  // send in the register address - 5 bits LSB
  jtag_goto_shift_dr();
  temp = jtagtransn(reg, 5, LSB| NOEND| NORETIDLE);
  
  // clear TDI to select "read only"
  jtagtransn(0L, 1, LSB);
  
  jtag_goto_shift_dr();
  // Now shift out the 32 bits
  retval = jtagtransn(0L, 32, LSB);   // atmel arm jtag docs pp.10-11: LSB first
  //debughex32(retval);
  return(retval);   // atmel arm jtag docs pp.10-11: LSB first
  
}




/************************* ICEBreaker/EmbeddedICE Stuff ******************************/
//! Grab debug register
unsigned long jtagarm7tdmi_get_dbgstate() {       // ICE Debug register, *NOT* ARM register DSCR    //    PROVEN
  //jtagarm7tdmi_resettap();
  return eice_read(EICE_DBGSTATUS);
}

//! Grab debug register
unsigned long jtagarm7tdmi_get_dbgctrl() {
  return eice_read(EICE_DBGCTRL);
}

//! Update debug register
unsigned long jtagarm7tdmi_set_dbgctrl(unsigned long bits) {
  return eice_write(EICE_DBGCTRL, bits);
}



//!  Set and Enable Watchpoint 0
void jtagarm7tdmi_set_watchpoint0(unsigned long addr, unsigned long addrmask, unsigned long data, unsigned long datamask, unsigned long ctrl, unsigned long ctrlmask){
  // store watchpoint info?  - not right now
    // FIXME: store info

  eice_write(EICE_WP0ADDR, addr);           // write 0 in watchpoint 0 address
  eice_write(EICE_WP0ADDRMASK, addrmask);   // write 0xffffffff in watchpoint 0 address mask
  eice_write(EICE_WP0DATA, data);           // write 0 in watchpoint 0 data
  eice_write(EICE_WP0DATAMASK, datamask);   // write 0xffffffff in watchpoint 0 data mask
  eice_write(EICE_WP0CTRL, ctrlmask);       // write 0x00000100 in watchpoint 0 control value register (enables watchpoint)
  eice_write(EICE_WP0CTRLMASK, ctrlmask);   // write 0xfffffff7 in watchpoint 0 control mask - only detect the fetch instruction
}

//!  Set and Enable Watchpoint 1
void jtagarm7tdmi_set_watchpoint1(unsigned long addr, unsigned long addrmask, unsigned long data, unsigned long datamask, unsigned long ctrl, unsigned long ctrlmask){
  // store watchpoint info?  - not right now
    // FIXME: store info

  eice_write(EICE_WP1ADDR, addr);           // write 0 in watchpoint 1 address
  eice_write(EICE_WP1ADDRMASK, addrmask);   // write 0xffffffff in watchpoint 1 address mask
  eice_write(EICE_WP1DATA, data);           // write 0 in watchpoint 1 data
  eice_write(EICE_WP1DATAMASK, datamask);   // write 0xffffffff in watchpoint 1 data mask
  eice_write(EICE_WP1CTRL, ctrl);           // write 0x00000100 in watchpoint 1 control value register (enables watchpoint)
  eice_write(EICE_WP1CTRLMASK, ctrlmask);   // write 0xfffffff7 in watchpoint 1 control mask - only detect the fetch instruction
}

/******************** Complex Commands **************************/

//! Retrieve a 32-bit Register value
unsigned long jtagarm7tdmi_get_register(unsigned long reg) {                    //PROVEN
  unsigned long retval=0L, instr;
  if (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT)
    instr = THUMB_INSTR_STR_R0_r0 | reg | (reg<<16);
  else
    instr = (unsigned long)(reg<<12L) | (unsigned long)ARM_READ_REG;   // STR Rx, [R14] 

  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_instr_primitive(instr, 0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  retval = jtagarm7tdmi_nop( 0);                        // recover 32-bit word
  return retval;
}

//! Set a 32-bit Register value
void jtagarm7tdmi_set_register(unsigned long reg, unsigned long val) {          // PROVEN (assuming target reg is word aligned)
  unsigned long instr;
  //if (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT)
    //instr = THUMB_WRITE_REG
    instr = (unsigned long)(((unsigned long)reg<<12L) | ARM_WRITE_REG); //  LDR Rx, [R14]
  
  jtagarm7tdmi_nop( 0);            // push nop into pipeline - clean out the pipeline...
  jtagarm7tdmi_nop( 0);            // push nop into pipeline - clean out the pipeline...
  jtagarm7tdmi_instr_primitive(instr, 0); // push instr into pipeline - fetch
  if (reg == ARM_REG_PC){
    jtagarm7tdmi_instr_primitive(val, 0); // push 32-bit word on data bus
    jtagarm7tdmi_nop( 0);            // push nop into pipeline - executed 
    jtagarm7tdmi_nop( 0);            // push nop into pipeline - executed 
  } else {
    jtagarm7tdmi_nop( 0);            // push nop into pipeline - decode
    jtagarm7tdmi_nop( 0);            // push nop into pipeline - execute
    jtagarm7tdmi_instr_primitive(val, 0); // push 32-bit word on data bus
  }
  jtagarm7tdmi_nop( 0);            // push nop into pipeline - executed 
  jtagarm7tdmi_nop( 0);            // push nop into pipeline - executed 
  jtagarm7tdmi_nop( 0);
}


/*
//! Get all registers, placing them into cmddatalong[0-14]
void jtagarm7tdmi_get_registers() {         // BORKEN.  FIXME
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_instr_primitive(ARM_INSTR_SKANKREGS,0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  cmddatalong[ 0] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 1] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 2] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 3] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 4] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 5] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 6] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 7] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 8] = jtagarm7tdmi_nop( 0);
  cmddatalong[ 9] = jtagarm7tdmi_nop( 0);
  cmddatalong[10] = jtagarm7tdmi_nop( 0);
  cmddatalong[11] = jtagarm7tdmi_nop( 0);
  cmddatalong[12] = jtagarm7tdmi_nop( 0);
  cmddatalong[13] = jtagarm7tdmi_nop( 0);
  cmddatalong[14] = jtagarm7tdmi_nop( 0);
  cmddatalong[15] = jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
}

//! Set all registers from cmddatalong[0-14]
void jtagarm7tdmi_set_registers() {   // using r15 to write through.  not including it.  use set_pc
  jtagarm7tdmi_nop( 0);
  debughex32(jtagarm7tdmi_instr_primitive(ARM_INSTR_CLOBBEREGS,0));
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_nop( 0);
  jtagarm7tdmi_instr_primitive(cmddatalong[0],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[1],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[2],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[3],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[4],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[5],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[6],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[7],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[8],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[9],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[10],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[11],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[12],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[13],0);
  jtagarm7tdmi_instr_primitive(cmddatalong[14],0);
  jtagarm7tdmi_nop( 0);
}
*/
//! Retrieve the CPSR Register value
unsigned long jtagarm7tdmi_get_regCPSR() {
  unsigned long retval = 0L, r0;

  r0 = jtagarm7tdmi_get_register(0);
  jtagarm7tdmi_nop( 0); // push nop into pipeline - clean out the pipeline...
  jtagarm7tdmi_instr_primitive(ARM_INSTR_MRS_R0_CPSR, 0); // push MRS_R0, CPSR into pipeline - fetch
  jtagarm7tdmi_nop( 0); // push nop into pipeline - decoded
  jtagarm7tdmi_nop( 0); // push nop into pipeline - execute
  retval = jtagarm7tdmi_get_register(0);
  jtagarm7tdmi_set_register(0, r0);
  return retval;
}

//! Retrieve the CPSR Register value
unsigned long jtagarm7tdmi_set_regCPSR(unsigned long val) {
  unsigned long r0;

  r0 = jtagarm7tdmi_get_register(0);
  jtagarm7tdmi_set_register(0, val);
  debughex32(jtagarm7tdmi_nop( 0));        // push nop into pipeline - clean out the pipeline...
  debughex32(jtagarm7tdmi_instr_primitive(ARM_INSTR_MSR_cpsr_cxsf_R0, 0)); // push MSR cpsr_cxsf, R0 into pipeline - fetch
  debughex32(jtagarm7tdmi_nop( 0));        // push nop into pipeline - decoded
  debughex32(jtagarm7tdmi_nop( 0));        // push nop into pipeline - execute
  jtagarm7tdmi_set_register(0, r0);
  return(val);
}

unsigned long wait_debug(unsigned long retval){
  // Poll the Debug Status Register for DBGACK and nMREQ to be HIGH
  current_dbgstate = jtagarm7tdmi_get_dbgstate();
  while ((!(current_dbgstate & 9L) == 9)  && retval > 0){
    delay(1);
    retval --;
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
  }
  return retval;
}

/****
//! Write data to address - Assume TAP in run-test/idle state
unsigned long jtagarm7tdmi_writemem(unsigned long adr, unsigned long data){
  unsigned long retval = 0xffL;
  unsigned long r0=0L, r1=-1L;

  r0 = jtagarm7tdmi_get_register(0);        // store R0 and R1
  r1 = jtagarm7tdmi_get_register(1);
  jtagarm7tdmi_set_register(0, adr);        // write address into R0
  jtagarm7tdmi_set_register(1, data);       // write data in R1
  debughex32(jtagarm7tdmi_get_register(0));
  debughex32(jtagarm7tdmi_get_register(1));
  jtagarm7tdmi_nop( 0);                     // push nop into pipeline to "clean" it ???
  jtagarm7tdmi_nop( 1);                     // push nop into pipeline with BREAKPT set
  jtagarm7tdmi_instr_primitive(ARM_INSTR_STR_R1_r0_4, 0); // push LDR R1, R0, #4 into instruction pipeline
  jtagarm7tdmi_nop( 0);                     // push nop into pipeline
  jtagarm7tdmi_restart();                   // SHIFT_IR with RESTART instruction

  if (wait_debug(0xffL) == 0){
    debugstr("FAILED TO WRITE MEMORY/RE-ENTER DEBUG MODE");
    return (-1);
  } else {
    retval = jtagarm7tdmi_get_register(1);  // read memory value from R1 register
    jtagarm7tdmi_set_register(1, r1);         // restore R0 and R1 
    jtagarm7tdmi_set_register(0, r0);
  }
  return retval;
}



//! Read data from address
unsigned long jtagarm7tdmi_readmem(unsigned long adr){
  unsigned long retval = 0xffL;
  unsigned long r0=0L, r1=-1L;

  r0 = jtagarm7tdmi_get_register(0);        // store R0 and R1
  r1 = jtagarm7tdmi_get_register(1);
  jtagarm7tdmi_set_register(0, adr);        // write address into R0
  jtagarm7tdmi_nop( 0);                     // push nop into pipeline to "clean" it ???
  jtagarm7tdmi_nop( 1);                     // push nop into pipeline with BREAKPT set
  jtagarm7tdmi_instr_primitive(ARM_INSTR_LDR_R1_r0_4, 0); // push LDR R1, [R0], #4 into instruction pipeline  (autoincrements for consecutive reads)
  jtagarm7tdmi_nop( 0);                     // push nop into pipeline
  jtagarm7tdmi_restart();                   // SHIFT_IR with RESTART instruction

  // Poll the Debug Status Register for DBGACK and nMREQ to be HIGH
  current_dbgstate = jtagarm7tdmi_get_dbgstate();
  debughex(current_dbgstate);
  while ((!(current_dbgstate & 9L) == 9)  && retval > 0){
    delay(1);
    retval --;
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
  }
  // FIXME: this may end up changing te current debug-state.  should we compare to current_dbgstate?
  if (retval == 0){
    debugstr("FAILED TO READ MEMORY/RE-ENTER DEBUG MODE");
    return (-1);
  } else {
    retval = jtagarm7tdmi_get_register(1);  // read memory value from R1 register
    //jtagarm7tdmi_set_register(1, r1);       // restore R0 and R1 
    //jtagarm7tdmi_set_register(0, r0);
  }
  return retval;
}

*/


//! Read Program Counter
unsigned long jtagarm7tdmi_get_real_pc(){
    unsigned long val;
    val = jtagarm7tdmi_get_register(ARM_REG_PC);
    if (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT)
        val -= (4*2);                           // thumb uses 2 bytes per instruction.
    else
        val -= (6*4);                           // assume 6 instructions at 4 bytes a piece.
    return val;
}

//! Halt CPU - returns 0xffff if the operation fails to complete within 
unsigned long jtagarm7tdmi_haltcpu(){                   //  PROVEN
  int waitcount = 0xffL;

  // store the debug state
  last_halt_debug_state = jtagarm7tdmi_get_dbgstate();

  //jtagarm7tdmi_set_dbgctrl(7);
  // store watchpoint info?  - not right now
  jtagarm7tdmi_set_watchpoint1(0, 0xffffffff, 0, 0xffffffff, 0x100L, 0xfffffff7);


  /*  // old method
  eice_write(EICE_WP1ADDR, 0L);              // write 0 in watchpoint 1 address
  eice_write(EICE_WP1ADDRMASK, 0xffffffff); // write 0xffffffff in watchpoint 1 address mask
  eice_write(EICE_WP1DATA, 0L);              // write 0 in watchpoint 1 data
  eice_write(EICE_WP1DATAMASK, 0xffffffff); // write 0xffffffff in watchpoint 1 data mask
  eice_write(EICE_WP1CTRL, 0x100L);          // write 0x00000100 in watchpoint 1 control value register (enables watchpoint)
  eice_write(EICE_WP1CTRLMASK, 0xfffffff7); // write 0xfffffff7 in watchpoint 1 control mask - only detect the fetch instruction
  */

  // poll until debug status says the cpu is in debug mode
  while (!(current_dbgstate & 0x1L)   && waitcount-- > 0){
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
    delay(1);
  }

  //jtagarm7tdmi_set_dbgctrl(0);
  jtagarm7tdmi_set_watchpoint1(0, 0x0, 0, 0x0, 0x0L, 0xfffffff7);
  //jtagarm7tdmi_disable_watchpoint1();

  //eice_write(EICE_WP1CTRL, 0x0L);            // write 0 in watchpoint 0 control value - disables watchpoint 0

  // store the debug state program counter.
  last_halt_pc = jtagarm7tdmi_get_real_pc();    // FIXME: grag chain0 to get all state and PC
  count_dbgspd_instr_since_debug = 0L;          // should be able to clean this up and remove all this tracking nonsense.
  count_sysspd_instr_since_debug = 0L;          // should be able to clean this up and remove all this tracking nonsense.

  //FIXME: is this necessary?  for now, yes... but perhaps make the rest of the module arm/thumb impervious.
  // get into ARM mode if the T flag is set (Thumb mode)
  while (current_dbgstate & JTAG_ARM7TDMI_DBG_TBIT && waitcount-- > 0) {
    jtagarm7tdmi_setMode_ARM(0);
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
  }
  jtagarm7tdmi_resettap();
  jtagarm7tdmi_set_register(ARM_REG_PC, last_halt_pc & 0xfffffffc);     // make sure PC is word-aligned.  otherwise all other register accesses get all wonky.
  return waitcount;
}

unsigned long jtagarm7tdmi_releasecpu(){
  int waitcount = 0xff;
  jtagarm7tdmi_nop(0);                          // NOP
  jtagarm7tdmi_nop(1);                          // NOP/BREAKPT


  // four possible states.  arm mode needing arm mode, arm mode needing thumb mode, thumb mode needing arm mode, and thumb mode needing thumb mode
  // FIXME:  BX is bs.  it requires the clobbering of at least one register.... this is not acceptable.  
  // FIXME:  so we either switch modes, then correct the register before restarting with bx, or find the way to use SPSR
  if (last_halt_debug_state & JTAG_ARM7TDMI_DBG_TBIT){
    // need to get to thumb mode
    jtagarm7tdmi_set_register(15,last_halt_pc-20);        // 20 bytes will be added to pc before the end of the write.  incorrect and must fix
    jtagarm7tdmi_setMode_THUMB(1);
  } else {
    jtagarm7tdmi_setMode_ARM(1);
    //jtagarm7tdmi_set_register(15,last_halt_pc-20);        // 20 bytes will be added to pc before the end of the write.  incorrect and must fix
  }


  jtagarm7tdmi_restart();
  jtagarm7tdmi_resettap();
  //jtag_goto_shift_ir();
  //jtagarmtransn(ARM7TDMI_IR_RESTART,4,LSB,END,RETIDLE); // VERB_RESTART

  // wait until restart-bit set in debug state register
  while ((current_dbgstate & JTAG_ARM7TDMI_DBG_DBGACK) && waitcount > -1){
    msdelay(1);
    waitcount --;
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
  }
  last_halt_debug_state = -1;
  last_halt_pc = -1;
  return waitcount;
}
 



///////////////////////////////////////////////////////////////////////////////////////////////////
//! Handles ARM7TDMI JTAG commands.  Forwards others to JTAG.
void jtagarm7tdmihandle(unsigned char app, unsigned char verb, unsigned long len){
  //register char blocks;
  
  unsigned int val; //, i;
  //unsigned long at;
  
  //jtagarm7tdmi_resettap();
  //current_dbgstate = jtagarm7tdmi_get_dbgstate();
 
  switch(verb){
  case START:
    //Enter JTAG mode.
    debughex32(jtagarm7tdmi_start());
    cmddatalong[0] = jtagarm7tdmi_get_dbgstate();
    txdata(app,verb,0x4);
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
    break;
    /*
  case JTAGARM7TDMI_READMEM:
    at     = cmddatalong[0];
    blocks = cmddatalong[1];
    
    txhead(app,verb,len);
    
	jtagarm7tdmi_resettap();
	delay(1);
	
    for(i=0;i<blocks;i++){
	  val=jtagarm7tdmi_readmem(at);
		
 	  serial_tx(val&0xFFL);
	  serial_tx((val&0xFF00L)>>8);
	  serial_tx((val&0xFF0000L)>>8);
	  serial_tx((val&0xFF000000L)>>8);
  	  at+=4;
      }
    
    
    break;
  case PEEK:
	jtagarm7tdmi_resettap();
	delay(1);
	cmddatalong[0] = jtagarm7tdmi_readmem(cmddatalong[0]);
    txdata(app,verb,4);
    break;
    */
  case JTAGARM7TDMI_GET_CHIP_ID:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_idcode();
    txdata(app,verb,4);
    break;

/*
  case JTAGARM7TDMI_WRITEMEM:
  case POKE:
	jtagarm7tdmi_resettap();
    jtagarm7tdmi_writemem(cmddatalong[0],
		       cmddataword[2]);
    cmddataword[0]=jtagarm7tdmi_readmem(cmddatalong[0]);
    txdata(app,verb,4);
    break;
*/
  case JTAGARM7TDMI_HALTCPU:  
    cmddatalong[0] = jtagarm7tdmi_haltcpu();
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_RELEASECPU:
	//jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_releasecpu();
    txdata(app,verb,4);
    break;
  //unimplemented functions
  //case JTAGARM7TDMI_SETINSTRFETCH:
  //case JTAGARM7TDMI_WRITEFLASH:
  //case JTAGARM7TDMI_ERASEFLASH:
  case JTAGARM7TDMI_SET_PC:
    //jtagarm7tdmi_setpc(cmddatalong[0]);
    last_halt_pc = cmddatalong[0];
    txdata(app,verb,0);
    break;
  case JTAGARM7TDMI_GET_DEBUG_CTRL:
    cmddatalong[0] = jtagarm7tdmi_get_dbgctrl();
    txdata(app,verb,1);
    break;
  case JTAGARM7TDMI_SET_DEBUG_CTRL:
    cmddatalong[0] = jtagarm7tdmi_set_dbgctrl(cmddata[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_GET_PC:
    cmddatalong[0] = last_halt_pc;
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_GET_DEBUG_STATE:
    //jtagarm7tdmi_resettap();            // Shouldn't need this, but currently do.  FIXME!
    current_dbgstate = jtagarm7tdmi_get_dbgstate();
    cmddatalong[0] = current_dbgstate;
    txdata(app,verb,4);
    break;
  //case JTAGARM7TDMI_GET_WATCHPOINT:
  //case JTAGARM7TDMI_SET_WATCHPOINT:
  case JTAGARM7TDMI_GET_REGISTER:
	//jtagarm7tdmi_resettap();
    val = cmddata[0];
    cmddatalong[0] = jtagarm7tdmi_get_register(val);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_REGISTER:
	//jtagarm7tdmi_resettap();
    jtagarm7tdmi_set_register(cmddatalong[1], cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_DEBUG_INSTR:
	//jtagarm7tdmi_resettap();
    //cmddataword[0] = jtagarm7tdmi_exec(cmddataword[0], cmddata[4]);
    cmddatalong[0] = jtagarm7tdmi_instr_primitive(cmddatalong[0],cmddata[4]);
    txdata(app,verb,8);
    break;
  //case JTAGARM7TDMI_STEP_INSTR:
/*  case JTAGARM7TDMI_READ_CODE_MEMORY:
  case JTAGARM7TDMI_WRITE_FLASH_PAGE:
  case JTAGARM7TDMI_READ_FLASH_PAGE:
  case JTAGARM7TDMI_MASS_ERASE_FLASH:
  case JTAGARM7TDMI_PROGRAM_FLASH:
  case JTAGARM7TDMI_LOCKCHIP:
  case JTAGARM7TDMI_CHIP_ERASE:
  */
// Really ARM specific stuff
  case JTAGARM7TDMI_GET_CPSR:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_get_regCPSR();
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_CPSR:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_set_regCPSR(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_GET_SPSR:           // FIXME: NOT EVEN CLOSE TO CORRECT
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_get_regCPSR();
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_SPSR:           // FIXME: NOT EVEN CLOSE TO CORRECT
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_set_regCPSR(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_MODE_THUMB:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_setMode_THUMB(cmddata[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_MODE_ARM:
	jtagarm7tdmi_resettap();
    cmddatalong[0] = jtagarm7tdmi_setMode_ARM(cmddata[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SET_IR:
	//jtagarm7tdmi_resettap();
    jtag_goto_shift_ir();
    cmddataword[0] = jtagtransn(cmddata[0], 4, cmddata[1]);
    current_chain = -1;
    txdata(app,verb,2);
    break;
  case JTAGARM7TDMI_WAIT_DBG:
    cmddatalong[0] = wait_debug(cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SHIFT_DR:
	jtagarm7tdmi_resettap();
    jtag_goto_shift_dr();
    cmddatalong[0] = jtagtransn(cmddatalong[1],cmddata[0],cmddata[1]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_CHAIN0:
    jtagarm7tdmi_scan_intest(0);
    jtag_goto_shift_dr();
    debughex32(cmddatalong[0]);
    debughex(cmddataword[4]);
    debughex32(cmddatalong[1]);
    debughex32(cmddatalong[3]);
    cmddatalong[0] = jtagtransn(cmddatalong[0], 32, LSB| NOEND| NORETIDLE);
    cmddatalong[2] = jtagtransn(cmddataword[4], 9, MSB| NOEND| NORETIDLE);
    cmddatalong[1] = jtagtransn(cmddatalong[1], 32, MSB| NOEND| NORETIDLE);
    cmddatalong[3] = jtagtransn(cmddatalong[3], 32, MSB);
    txdata(app,verb,16);
    break;
  case JTAGARM7TDMI_SETWATCH0:
    jtagarm7tdmi_set_watchpoint0(cmddatalong[0], cmddatalong[1], cmddatalong[2], cmddatalong[3], cmddatalong[4], cmddatalong[5]);
    txdata(app,verb,4);
    break;
  case JTAGARM7TDMI_SETWATCH1:
    jtagarm7tdmi_set_watchpoint0(cmddatalong[0], cmddatalong[1], cmddatalong[2], cmddatalong[3], cmddatalong[4], cmddatalong[5]);
    txdata(app,verb,4);
    break;
  default:
    jtaghandle(app,verb,len);
  }
}




/*****************************
Captured from FlySwatter against AT91SAM7S, to be used by me for testing.  ignore

> arm reg
System and User mode registers
      r0: 300000df       r1: 00000000       r2: 58000000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 000000fc
    cpsr: 00000093

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000000 spsr_abt: e00000ff

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
> 
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Supervisor
cpsr: 0x00000093 pc: 0x00000100
System and User mode registers
      r0: 300000df       r1: 00000000       r2: 00200000       r3: 00200a75 
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c 
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000 
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000100 
    cpsr: 00000093 

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000 
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb 

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3 

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000000 spsr_abt: e00000ff 

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b 

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df 
> 
 step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75 
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c 
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000 
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010 
    cpsr: 00000097 

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000 
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb 

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3 

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093 

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b 

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df 
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75 
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c 
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000 
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010 
    cpsr: 00000097 

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000 
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb 

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3 

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093 

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b 

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df 
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010
    cpsr: 00000097

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010
    cpsr: 00000097

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010
    cpsr: 00000097

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010
    cpsr: 00000097

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010
    cpsr: 00000097

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010
    cpsr: 00000097

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
> step;arm reg
target state: halted
target halted in ARM state due to single-step, current mode: Abort
cpsr: 0x00000097 pc: 0x00000010
System and User mode registers
      r0: 300000e3       r1: 00000000       r2: 00200000       r3: 00200a75
      r4: fffb0000       r5: 00000002       r6: 00000000       r7: 00200f6c
      r8: 00000000       r9: 00000000      r10: ffffffff      r11: 00000000
     r12: 00000009   sp_usr: 00000000   lr_usr: 00000000       pc: 00000010
    cpsr: 00000097

FIQ mode shadow registers
  r8_fiq: 00000000   r9_fiq: fffcc000  r10_fiq: fffff400  r11_fiq: fffff000
 r12_fiq: 00200f44   sp_fiq: 00000000   lr_fiq: 00000000 spsr_fiq: f00000fb

Supervisor mode shadow registers
  sp_svc: 00201f78   lr_svc: 00200a75 spsr_svc: 400000b3

Abort mode shadow registers
  sp_abt: 00000000   lr_abt: 00000108 spsr_abt: 00000093

IRQ mode shadow registers
  sp_irq: 00000000   lr_irq: 00000000 spsr_irq: f000003b

Undefined instruction mode shadow registers
  sp_und: 00000000   lr_und: 00000000 spsr_und: 300000df
>
*/
