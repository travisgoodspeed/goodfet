/*! \file jtagarm7tdmi.h
  \brief JTAG handler functions for the ARM family of processors
*/

#include "jtag.h"


#define JTAGSTATE_ARM 0         // bit 4 on dbg status reg is low
#define JTAGSTATE_THUMB 1

unsigned long last_instr = -1;
unsigned char last_sysstate = 0;
unsigned char last_ir = -1;
unsigned char last_scanchain = -1;
unsigned char tapstate = 15;
unsigned char current_dbgstate = -1;
//unsigned char last_halt_debug_state = -1;
//unsigned long last_halt_pc = -1;


// JTAGARM7 Commands

//! Start JTAG
void adiv5_start(void);

//!  Set a 32-bit ARM register
void jtagarm7tdmi_set_register(unsigned long reg, unsigned long val);
//!  Get a 32-bit ARM register
unsigned long jtagarm7tdmi_get_register(unsigned long reg);

// ARM-specific pins
// DBGRQ - GoodFET Pin 8
#define DBGRQ   TST

/*      ARM data
The instruction register is 4 bits in length.
There is no parity bit.
The fixed value 0001 is loaded into the instruction register during the CAPTURE-IR
controller state.
The least significant bit of the instruction register is scanned in and scanned out first.
*/

//4-bit ARM JTAG INSTRUCTIONS - STANDARD
#define ADI_IR_ABORT                0x8
#define ADI_IR_RESERVED1            0x9
#define ADI_IR_DPACC                0xA
#define ADI_IR_APACC                0xB
#define ADI_IR_RESERVED2            0xC
#define ADI_IR_RESERVED3            0xD
#define ADI_IR_IDCODE               0xE
#define ADI_IR_BYPASS               0xF


//4-bit ARM JTAG INSTRUCTIONS - IMPLEMENTATION-DEFINED
#define ADI_IR_EXTEST               0x0
#define ADI_IR_SAMPLE               0x1
#define ADI_IR_PRELOAD              0x2
#define ADI_IR_RESERVED             0x3
#define ADI_IR_INTEST               0x4
#define ADI_IR_CLAMP                0x5
#define ADI_IR_HIGHZ                0x6
#define ADI_IR_CLAMPZ               0x7

// read 3 bit - Debug Control
#define EICE_DBGCTRL                    0       
#define EICE_DBGCTRL_BITLEN             3
// read 5 bit - Debug Status
#define EICE_DBGSTATUS                  1
#define EICE_DBGSTATUS_BITLEN           5
// read 6 bit - Debug Comms Control Register
#define EICE_DBGCCR                     4
#define EICE_DBGCCR_BITLEN              6
// r/w 32 bit - Debug Comms Data Register
#define EICE_DBGCDR                     5
// r/w 32 bit - Watchpoint 0 Address
#define EICE_WP0ADDR                    8
// r/w 32 bit - Watchpoint 0 Addres Mask
#define EICE_WP0ADDRMASK                9
// r/w 32 bit - Watchpoint 0 Data
#define EICE_WP0DATA                    10
// r/w 32 bit - Watchpoint 0 Data Masl
#define EICE_WP0DATAMASK                11
// r/w 9 bit - Watchpoint 0 Control Value
#define EICE_WP0CTRL                    12
// r/w 8 bit - Watchpoint 0 Control Mask
#define EICE_WP0CTRLMASK                13
// r/w 32 bit - Watchpoint 0 Address
#define EICE_WP1ADDR                    16
// r/w 32 bit - Watchpoint 0 Addres Mask
#define EICE_WP1ADDRMASK                17
// r/w 32 bit - Watchpoint 0 Data
#define EICE_WP1DATA                    18
// r/w 32 bit - Watchpoint 0 Data Masl
#define EICE_WP1DATAMASK                19
// r/w 9 bit - Watchpoint 0 Control Value
#define EICE_WP1CTRL                    20
// r/w 8 bit - Watchpoint 0 Control Mask
#define EICE_WP1CTRLMASK                21


//JTAGARM commands
#define JTAGARM7_GET_REGISTER               0x87
#define JTAGARM7_SET_REGISTER               0x88
#define JTAGARM7_DEBUG_INSTR                0x89
// Really ARM specific stuff
#define JTAGARM7_SET_IR                     0x90
#define JTAGARM7_WAIT_DBG                   0x91
#define JTAGARM7_SHIFT_DR                   0x92
#define JTAGARM7_CHAIN0                     0x93
#define JTAGARM7_SCANCHAIN1                 0x94
#define JTAGARM7_EICE_READ                  0x95
#define JTAGARM7_EICE_WRITE                 0x96


// for deeper understanding, read the instruction cycle timing section of: 
//      http://www.atmel.com/dyn/resources/prod_documents/DDI0029G_7TDMI_R3_trm.pdf
#define EXECNOPARM                  0xe1a00000L
#define ARM_INSTR_NOP               0xe1a00000L
#define ARM_INSTR_BX_R0             0xe12fff10L
#define ARM_INSTR_STR_Rx_r14        0xe58f0000L // from atmel docs
#define ARM_READ_REG                ARM_INSTR_STR_Rx_r14
#define ARM_INSTR_LDR_Rx_r14        0xe5900000L // NOT from atmel docs (e59e0000L is from atmel docs)
#define ARM_WRITE_REG               ARM_INSTR_LDR_Rx_r14
#define ARM_INSTR_LDR_R1_r0_4       0xe4901004L
#define ARM_READ_MEM                ARM_INSTR_LDR_R1_r0_4
#define ARM_INSTR_STR_R1_r0_4       0xe4801004L
#define ARM_WRITE_MEM               ARM_INSTR_STR_R1_r0_4
#define ARM_INSTR_MRS_R0_CPSR       0xe10f0000L
#define ARM_INSTR_MSR_cpsr_cxsf_R0  0xe12ff000L
#define ARM_INSTR_STMIA_R14_r0_rx   0xE88E0000L      // add up to 65k to indicate which registers...
#define ARM_STORE_MULTIPLE          ARM_INSTR_STMIA_R14_r0_rx
#define ARM_INSTR_SKANKREGS         0xE88F7fffL
#define ARM_INSTR_CLOBBEREGS        0xE89F7fffL

#define ARM_INSTR_B_IMM             0xea000000L
#define ARM_INSTR_BX_PC             0xe12fff10L      // need to set r0 to the desired address
#define THUMB_INSTR_LDR_R0_r0       0x68006800L
#define THUMB_WRITE_REG             THUMB_INSTR_LDR_R0_r0
#define THUMB_INSTR_STR_R0_r0       0x60006000L
#define THUMB_READ_REG              THUMB_INSTR_STR_R0_r0
#define THUMB_INSTR_MOV_R0_PC       0x46b846b8L
#define THUMB_INSTR_MOV_PC_R0       0x46474647L
#define THUMB_INSTR_MOV_HiLo        0x46404640L
#define THUMB_INSTR_MOV_LoHi        0x46804680L
#define THUMB_INSTR_BX_PC           0x47784778L
#define THUMB_INSTR_NOP             0x1c001c00L
#define THUMB_SWAP_HiLo             0
#define THUMB_SWAP_LoHi             1
#define ARM_REG_PC                  15

#define JTAG_ARM_DBG_DBGACK    1
#define JTAG_ARM_DBG_DBGRQ     2
#define JTAG_ARM_DBG_IFEN      4
#define JTAG_ARM_DBG_cgenL     8
#define JTAG_ARM_DBG_TBIT      16

