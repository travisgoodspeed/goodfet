/*! \file ejtag.h
  \author Travis Goodspeed <travis at radiantmachines.com>
  \brief MIPS EJTAG IR/DR definitions
*/

#ifndef EJTAG_H
#define EJTAG_H

#define EJTAG 0x12

/* The following are standard EJTAG IR values.  TCBCONTROL values,
   reserved values, and device-specific values have been ommitted.
 */
#define EJTAG_IR_IDCODE 0x01
#define EJTAG_IR_IMPCODE 0x03
#define EJTAG_IR_ADDRESS 0x08
#define EJTAG_IR_DATA 0x09
#define EJTAG_IR_CONTROL 0x0A 
#define EJTAG_IR_ALL 0x0B
#define EJTAG_IR_EJTAGBOOT 0x0C
#define EJTAG_IR_NORMALBOOT 0x0D
#define EJTAG_IR_FASTDATA 0x0E
#define EJTAG_IR_PCSAMPLE 0x14
#define EJTAG_IR_BYPASS 0xFF

extern app_t const ejtag_app;

#endif

