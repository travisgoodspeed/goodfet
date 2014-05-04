/*! \file avr.h
  \author Travis Goodspeed
  \brief AVR SPI Programmer
*/

#ifndef AVR_H
#define AVR_H

#include "spi.h"
#include "app.h"

/* AVR is a known macro for the AVR C includes */
#define XAVR 0x32

//! Setup the AVR pins.
void avrsetup();

//! Initialized an attached AVR.
void avrconnect();

//! Enable AVR programming mode.
void avr_prgen();
//! Read AVR device code.
uint8_t avr_sig(uint8_t i);
//! Erase an AVR device
void avr_erase();
//! Read lock bits.
uint8_t avr_lockbits();
//! Write lock bits.
void avr_setlock(uint8_t bits);

//! Read a byte of Flash
uint8_t avr_peekflash(uint16_t adr);

//! Read a byte of EEPROM.
uint8_t avr_peekeeprom(uint16_t adr);
//! Read a byte of EEPROM.
uint8_t avr_pokeeeprom(uint16_t adr, uint8_t val);

//! Is the AVR ready or busy?
uint8_t avr_isready();

//Command codes.
//! Perform a chip erase.
#define AVR_ERASE 0xF0
//! Fetch RDY/!BSY byte.
#define AVR_RDYBSY 0xF1

//! Read Program Memory
#define AVR_PEEKPGM 0x80
//! Read EEPROM
#define AVR_PEEKEEPROM 0x81
//! Write EEPROM
#define AVR_POKEEEPROM 0x91
//! Read lock bits.
#define AVR_PEEKLOCK 0x82
//! Write lock its.
#define AVR_POKELOCK 0x92
//! Read signature.
#define AVR_PEEKSIG 0x83
//! Read fuse bits.
#define AVR_READFUSES 0x84
//! Read calibration byte.
#define AVR_READCAL 0x85
//! Bulk load data
#define AVR_BULKLOAD 0x86

extern app_t const avr_app;

#endif // AVR_H
