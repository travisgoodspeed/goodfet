/*! \file sbw.h
  \author Travis Goodspeed and Mark Rages
  \brief Spy-Bi-Wire Stuff
*/

#ifndef SBW_H
#define SBW_H

#include "app.h"
extern app_t const sbw_app;

#define SBW 0x17

#include "platform.h"
#include "command.h"
#include "app.h"

//IO Pins; these are for EZ430, not GoodFET/UIF
#define SBWTCK  BIT3
#define SBWTDIO BIT2

//This should be universal, move to jtag.h
#define TCKTOCK CLRTCK,SETTCK

//If SBW is defined, rewrite JTAG functions to be SBW.
#ifdef SBWREWRITE
#define jtagsetup sbwsetup

// I/O Redefintions
extern int tms, tdi, tdo;
#undef SETTMS
#define SETTMS tms=1
#undef CLRTMS
#define CLRTMS tms=0
#undef SETTDI
#define SETTDI tdi=1
#undef CLRTDI
#define CLRTDI tdi=0
#undef TCKTOCK
#define TCKTOCK clock_sbw()
#undef SETMOSI
#define SETMOSI SETTDI
#undef CLRMOSI
#define CLRMOSI CLRTDI
#undef READMISO
#define READMISO tdo

#endif

//! Enter SBW mode.
void sbwsetup();

//! Handle a SBW request.
void sbw_handler_fn(u8 app, u8 verb, u32 len);

//! Perform a SBW bit transaction.
void clock_sbw();
//! Set the TCLK line, performing a transaction.
void sbwSETTCLK();
//! Clear the line.
void sbwCLRTCLK();

// Macros
#define SBWCLK() do { \
    SPIOUT &= ~SBWTCK; \
    asm("nop");	      \
    asm("nop");	      \
    asm("nop");	      \
    SPIOUT |= SBWTCK;  \
  } while (0)
#define SETSBWIO(x) do { 			\
  if (x)					\
    SPIOUT |= SBWTDIO;				\
  else						\
    SPIOUT &= ~SBWTDIO;				\
  } while (0)
#undef RESTORETCLK
#define RESTORETCLK do {			\
    if(savedtclk) {				\
      SETTCLK; 					\
    } else {					\
      CLRTCLK;					\
    }						\
  } while (0);
#undef SETTCLK
#define SETTCLK do {				\
    sbwSETTCLK();				\
    savedtclk=1;				\
  } while (0);
#undef CLRTCLK
#define CLRTCLK do {				\
    sbwCLRTCLK();				\
    savedtclk=0;				\
  } while (0); 

#undef SAVETCLK
//Do nothing for this.
#define SAVETCLK 

#endif // SBW_H

