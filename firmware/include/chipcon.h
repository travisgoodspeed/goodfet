/*! \file chipcon.h
  \author Travis Goodspeed
  \brief Chipcon application functions.
*/

#ifndef CHIPCON_H
#define CHIPCON_H

#include "command.h"
#include "app.h"

#define CHIPCON 0x30

//Chipcon command definitions.
#define CCCMD_CHIP_ERASE 0x14

//1D or 19?
#define CCCMD_WR_CONFIG 0x1D
#define CCCMD_RD_CONFIG 0x24
#define CCCMD_READ_STATUS 0x34
#define CCCMD_GET_CHIP_ID 0x68
#define CCCMD_GET_PC 0x28
#define CCCMD_HALT 0x44
#define CCCMD_RESUME 0x4C
#define CCCMD_STEP_INSTR 0x5C
#define CCCMD_DEBUG_INSTR 0x54

//! Flash Word Size
extern u8 flash_word_size;

//! Erase a chipcon chip.
void cc_chip_erase();
//! Write the configuration byte.
void cc_wr_config(unsigned char config);
//! Read the configuration byte.
unsigned char cc_rd_config();
//! Read the status register.
unsigned char cc_read_status();
//! Read the CHIP ID bytes.
unsigned short cc_get_chip_id();
//! Get the PC
unsigned short cc_get_pc();
//! Set a hardware breakpoint.
void cc_set_hw_brkpnt(unsigned short);
//! Debug an instruction, for remote use.
void cc_debug_instr(unsigned char);
//!Read a byte of code memory.
unsigned char cc_peekcodebyte(unsigned long adr);
//!Read a byte of data memory.
unsigned char cc_peekdatabyte(unsigned int adr);
//! Fetch a byte of IRAM.
u8 cc_peekirambyte(u8 adr);
//! Write a byte of IRAM.
u8 cc_pokeirambyte(u8 adr, u8 val);
//! Set a byte of data memory.
unsigned char cc_pokedatabyte(unsigned int adr,
			      unsigned char val);
//! Debug an instruction, for local use.
unsigned char cc_debug(unsigned char len,
		       unsigned char a,
		       unsigned char b,
		       unsigned char c);

//! Populates flash buffer in xdata.
void cc_write_flash_buffer(u8 *data, u16 len);
//! Populates flash buffer in xdata.
void cc_write_xdata(u16 adr, u8 *data, u16 len);
//! Copies flash buffer to flash.
void cc_write_flash_page(u32 adr);
//! Set the Chipcon's Program Counter
void cc_set_pc(u32 adr);

//! Halt the CPU.
void cc_halt();
//! Resume the CPU.
void cc_resume();
//! Step an instruction
void cc_step_instr();
//! Locks the chip.
void cc_lockchip();

#define CC_STATUS_ERASED 0x80
#define CC_STATUS_PCONIDLE 0x40
#define CC_STATUS_CPUHALTED 0x20
#define CC_STATUS_PM0 0x10
#define CC_STATUS_HALTSTATUS 0x08
#define CC_STATUS_LOCKED 0x04
#define CC_STATUS_OSCSTABLE 0x02
#define CC_STATUS_OVERFLOW 0x01

//CHIPCON commands
#define CC_CHIP_ERASE 0x80
#define CC_WR_CONFIG 0x81
#define CC_RD_CONFIG 0x82
#define CC_GET_PC 0x83
#define CC_READ_STATUS 0x84
#define CC_SET_HW_BRKPNT 0x85
#define CC_HALT 0x86
#define CC_RESUME 0x87
#define CC_DEBUG_INSTR 0x88
#define CC_STEP_INSTR 0x89
#define CC_STEP_REPLACE 0x8a
#define CC_GET_CHIP_ID 0x8b
//CHIPCON macros
#define CC_READ_CODE_MEMORY 0x90
#define CC_READ_XDATA_MEMORY 0x91
#define CC_WRITE_XDATA_MEMORY 0x92
#define CC_SET_PC 0x93
#define CC_CLOCK_INIT 0x94
#define CC_WRITE_FLASH_PAGE 0x95
#define CC_READ_FLASH_PAGE 0x96
#define CC_MASS_ERASE_FLASH 0x97
#define CC_PROGRAM_FLASH 0x98
#define CC_WIPEFLASHBUFFER 0x99
#define CC_LOCKCHIP 0x9A

extern app_t const chipcon_app;

#endif // CHIPCON_H
