/*! \file i2c.h
  \author Dave Huseby
  \brief i2c bus protocol functions.
*/

#ifndef I2C_H
#define I2C_H

#include "app.h"

#define I2C_APP 0x02
#define CMD_SCAN 0x80

extern app_t const i2c_app;

#endif

