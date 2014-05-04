/*! \file glitch.h
  \author Travis Goodspeed
  \brief Glitch handler functions.
*/

#ifndef GLITCH_H
#define GLITCH_H

#include "command.h"
#include "app.h"

#define GLITCH 0x71

//Command codes
#define GLITCHAPP      0x80
#define GLITCHVERB     0x81
#define GLITCHTIME     0x82
#define GLITCHVOLTAGES 0x90
#define GLITCHRATE     0x91


//! Setup glitching.
void glitchsetup();
//! Call this before the function to be glitched.
void glitchprime();

extern u16 glitchH, glitchL, glitchstate, glitchcount;

//! Glitch an application.
void glitchapp(u8 app);
//! Set glitching voltages.
void glitchvoltages(u16 gnd, u16 vcc);
//! Set glitching rate.
void glitchrate(u16 rate);

extern app_t const glitch_app;

#endif // GLITCH_H

