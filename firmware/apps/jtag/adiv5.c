// ARM Debug Interface version 5 (cortex and above)
// from the ARM Debug Interface v5 Architecture Specification (IHI 0031A) document:
// "Logically, the ARM Debug Interface (ADI) consists of:
//      * A number of registrs that are private to the ADI.  These are referred to as the Debug Access Port (DAP) Registers
//      * A means to access the DAP registers
//      * A means to access the debug registers of the debug components to which the ADI is connected
// ...
//  Because the DAP logically consists of two parts, the Debug Port and Access Ports, it must support two types of access:
//      * Access to the Debug Port (DP) registers.  This is provided by Debug Port accesses (DPACC).
//      * Access to Access Port (AP) registers.  This is provided by Access Port accesses (APACC).
//  An ADI can include multiple Access Ports."




//////// lower levels - "Debug Ports"////////
//// Serial Wire Debug protocol
// the sw-dp is based on the coresight serial wire interface and can be implemented as either a synchronous or async interface (yay!   *NOT*)
//
// swd protocol comms consists of a three-phase protocol:
//      * host-to-target packet req
//      * target-to-host ack
//      * data-transfer if necessary, either direction depending on the packet req.
//


//// JTAG debug protocol
//  as with arm7tdmi will soon be, we're going to live at Select DR state as home state.  this allows each transaction to finish to a known state.  it's more for mental peace more than anything, since the old way works... but the mental understanding that the tap may either be in exit2 or runtest/idle is a hack at best.
//
//


//////// mid-levels - resource interface, or "Access Ports" ////////            - elected for pythonyness
//  "An AP is responsible for accessing debug component registers such as processor debug logic, ETM and trace port registers.  These accesses are made in response to APACC accesses in a manner defined by the AP."
//  two such APs:
//      * MEM-AP
//      * JTAG-AP






///////////////////////////////////////////////////////////////////////////////////////////////////
//! Handles ARM7TDMI JTAG commands.  Forwards others to JTAG.
void adiv5handle(unsigned char app, unsigned char verb, unsigned long len){
  unsigned int val;
 
  switch(verb){
  case START:
    //Enter JTAG mode.
    adiv5_start();
    txdata(app,verb,0);
    break;
  case JTAG_IR_SHIFT:
    cmddataword[0] = jtagarm_shift_ir(cmddata[0], cmddata[1]);
    txdata(app,verb,1);
    break;
  case JTAG_DR_SHIFT:
    jtag_goto_shift_dr();
    if (cmddata[0]>32){
        val = cmddatalong[1];
        cmddatalong[0] = jtagtransn(cmddatalong[1],cmddata[0]-32,cmddata[1]|NOEND);
        cmddatalong[1] = jtagtransn(cmddatalong[2],32,cmddata[1]);
        txdata(app,verb,5);
    } else {
        cmddatalong[0] = jtagtransn(cmddatalong[1],cmddata[0],cmddata[1]);
        txdata(app,verb,5);
    }
    tapstate = (cmddata[1]&NORETIDLE)>0?Update_DR:RunTest_Idle;
    break;
  case JTAGADI_DEBUG_INSTR:
    cmddatalong[0] = adiv5_instr_primitive(cmddatalong[0],cmddata[4]);
    txdata(app,verb,4);
    break;
  case JTAGADI_GET_REGISTER:
    val = cmddata[0];
    cmddatalong[0] = adiv5_get_register(val);
    txdata(app,verb,4);
    break;
  case JTAGADI_SET_REGISTER:
    adiv5_set_register(cmddatalong[1], cmddatalong[0]);
    txdata(app,verb,4);
    break;
  case JTAG_RESETTARGET:
    debugstr("RESET TARGET");
    CLRTST;
    delay(cmddataword[0]);
    SETTST;
    txdata(app,verb,4);
    break;


  //case JTAGARM7_STEP_INSTR:
/*  case JTAGARM7_READ_CODE_MEMORY:
  case JTAGARM7_WRITE_FLASH_PAGE:
  case JTAGARM7_READ_FLASH_PAGE:
  case JTAGARM7_MASS_ERASE_FLASH:
  case JTAGARM7_PROGRAM_FLASH:
  case JTAGARM7_LOCKCHIP:
  case JTAGARM7_CHIP_ERASE:
  */
  default:
    jtaghandle(app,verb,len);
  }
}


