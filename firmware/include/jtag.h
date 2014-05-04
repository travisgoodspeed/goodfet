/*! \file jtag.h
  \author Travis Goodspeed
  \brief JTAG handler functions.
*/

#ifndef JTAG_H
#define JTAG_H

#include "app.h"

#define JTAG 0x10

//! All states in the JTAG TAP
enum eTAPState
{
	UNKNOWN				= 0x0000,
	TEST_LOGIC_RESET	= 0x0001,
	RUN_TEST_IDLE		= 0x0002,
	SELECT_DR_SCAN		= 0x0004,
	CAPTURE_DR			= 0x0008,
	SHIFT_DR			= 0x0010,
	EXIT1_DR			= 0x0020,
	PAUSE_DR			= 0x0040,
	EXIT2_DR			= 0x0080,
	UPDATE_DR			= 0x0100,
	SELECT_IR_SCAN		= 0x0200,
	CAPTURE_IR			= 0x0400,
	SHIFT_IR			= 0x0800,
	EXIT1_IR			= 0x1000,
	PAUSE_IR			= 0x2000,
	EXIT2_IR			= 0x4000,
	UPDATE_IR			= 0x8000
};

extern unsigned char jtagid;

//! the global state of the JTAG TAP
extern enum eTAPState jtag_state;

//! Returns true if we're in any of the data register states
int in_dr();
//! Returns true if we're in any of the instruction register states
int in_ir();
//! Returns true if we're in run-test-idle state
int in_run_test_idle();
//! Check the state
int in_state(enum eTAPState state);

//! jtag_trans_n flags
enum eTransFlags
{
	MSB					= 0x0,
	LSB					= 0x1,
	NOEND				= 0x2,
	NORETIDLE			= 0x4
};

//! Shift n bytes.
uint32_t jtag_trans_n(uint32_t word, 
					  uint8_t bitcount, 
					  enum eTransFlags flags);
//! Shift 8 bits in/out of selected register
uint8_t jtag_trans_8(uint8_t in);
//! Shift 16 bits in/out of selected register
uint16_t jtag_trans_16(uint16_t in);
//! Shift 8 bits of the IR.
uint8_t jtag_ir_shift_8(uint8_t in);
//! Shift 16 bits of the DR.
uint16_t jtag_dr_shift_16(uint16_t in);
//! Stop JTAG, release pins
void jtag_stop();
//! Setup the JTAG pin directions.
void jtag_setup();
//! Ratchet Clock Down and Up
void jtag_tcktock();
//! Reset the target device
void jtag_reset_target();
//! TAP RESET
void jtag_reset_tap();
//! Get into the Shift-IR or Shift-DR
void jtag_shift_register();
//! Get into Capture-IR state
void jtag_capture_ir();
//! Get into Capture-DR state
void jtag_capture_dr();
//! Get to Run-Test-Idle without going through Test-Logic-Reset
void jtag_run_test_idle();
//! Detect instruction register width
uint16_t jtag_detect_ir_width();
//! Detects how many TAPs are in the JTAG chain
uint16_t jtag_detect_chain_length();
//! Gets device ID for specified chip in the chain
uint32_t jtag_get_device_id(int chip);

//Pins.  Both SPI and JTAG names are acceptable.
//#define SS   BIT0
#define MOSI BIT1
#define MISO BIT2
#define SCK  BIT3

#define TMS BIT0
#define TDI BIT1
#define TDO BIT2
#define TCK BIT3

#define TCLK TDI

//These are not on P5
#define RST BIT6
#define TST BIT0

//This could be more accurate.
//Does it ever need to be?
#define JTAGSPEED 20
#define JTAGDELAY(x) delay(x)


#define SETMOSI SPIOUT|=MOSI
#define CLRMOSI SPIOUT&=~MOSI
#define SETCLK SPIOUT|=SCK
#define CLRCLK SPIOUT&=~SCK
#define READMISO (SPIIN&MISO?1:0)
#define SETTMS SPIOUT|=TMS
#define CLRTMS SPIOUT&=~TMS
#define SETTCK SPIOUT|=TCK
#define CLRTCK SPIOUT&=~TCK
#define SETTDI SPIOUT|=TDI
#define CLRTDI SPIOUT&=~TDI

#define SETTST P4OUT|=TST
#define CLRTST P4OUT&=~TST
#define SETRST P2OUT|=RST
#define CLRRST P2OUT&=~RST

#define SETTCLK SETTDI
#define CLRTCLK CLRTDI

extern int savedtclk;
#define SAVETCLK savedtclk=SPIOUT&TCLK;
#define RESTORETCLK if(savedtclk) SPIOUT|=TCLK; else SPIOUT&=~TCLK

//JTAG commands
#define JTAG_IR_SHIFT 0x80
#define JTAG_DR_SHIFT 0x81
#define JTAG_RESET_TAP 0x82
#define JTAG_RESET_TARGET 0x83
#define JTAG_DETECT_IR_WIDTH 0x84
#define JTAG_DETECT_CHAIN_LENGTH 0x85
#define JTAG_GET_DEVICE_ID 0x86
#define JTAG_DR_SHIFT_MORE 0x87 // used for shiftings > 32bits.  assumes JTAG_DR_SHIFT with NOEND first
//#define JTAG_DR_SHIFT20 0x91

extern app_t const jtag_app;

#endif
