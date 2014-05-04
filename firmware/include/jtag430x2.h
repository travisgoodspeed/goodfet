/*! \file jtag430x2.h
  \author Dave Huseby
  \brief MSP430X2 JTAG (20-bit)
*/

#ifndef JTAG430X2_H
#define JTAG430X2_H

#include "app.h"

#define JTAG430X2 0x11

extern app_t const jtag430x2_app;

//! Shift 20 bits of the DR.
uint32_t jtag430_dr_shift_20(uint32_t in);

#endif

