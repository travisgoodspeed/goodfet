/*! \file spi.h
  \author EiNSTeiN_ <einstein@g3nius.org>
  \brief Definitions for the Atmel 2-wire EEPROM application.
*/

#ifndef TWE_H
#define TWE_H

#include "app.h"

#define TWE 0x05

//Pins and I/O
#define SDA BIT1
#define SCL BIT3

#define SETSDA SPIOUT |= SDA
#define CLRSDA SPIOUT &= ~SDA
#define SETSCL SPIOUT |= SCL
#define CLRSCL SPIOUT &= ~SCL

//! Set up the pins for SPI mode.
void twe_setup();

//! Read and write an SPI byte.
unsigned char twe_trans8(unsigned char byte);

void twe_handle_fn( uint8_t const app,
					uint8_t const verb,
					uint32_t const len);

extern app_t const twe_app;

#endif /* TWE_H */
