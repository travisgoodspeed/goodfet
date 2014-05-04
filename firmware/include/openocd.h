/*! \file openocd.h
  \author Dave Huseby <dave at linuxprogrammer.org>
  \brief OpenOCD firmware
*/

#ifndef OPENOCD_H
#define OPENOCD_H

#include "app.h"

// OpenOCD app number
#define OPENOCD 0x18

// OpenOCD app verbs
#define OPENOCD_RESET	0x80
#define OPENOCD_READ	0x81
#define OPENOCD_WRITE	0x82
#define OPENOCD_LED		0x83

extern app_t const openocd_app;

#endif
