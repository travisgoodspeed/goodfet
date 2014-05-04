/*! \file z1.h
  \author Travis Goodspeed
  \brief Port descriptions for the Zolertia Z1 platform.
  
  This file defines the Zolertia hardware, so that the GoodFET firmware
  may be loaded onto it.  Adjustments are identical to the Telos B.

*/

#ifndef _GNU_ASSEMBLER_
#include <msp430.h>
#endif

//LED on P5.4 (LED1 red)
#define PLEDOUT P5OUT
#define PLEDDIR P5DIR
#define PLEDPIN BIT4
//LED on P5.5 (LED2 green)
#define PLED2OUT P5OUT
#define PLED2DIR P5DIR
#define PLED2PIN BIT5
//LED on P5.6 (LED3 blue)
#define PLED3OUT P5OUT
#define PLED3DIR P5DIR
#define PLED3PIN BIT6


#define SPIOUT P3OUT
#define SPIDIR P3DIR
#define SPIIN  P3IN
#define SPIREN P3REN


/* For the radio to be used:
   4.6 (!RST) must be low
   4.5 (VREF_EN) must be high
   4.2 (!CS) must be low for the transaction.
*/

#define INITPLATFORM \
  P1DIR = 0xe0;\
  P1OUT = 0x00;\
  P1REN = 0x0F;\
  P2DIR = 0x7b;\
  P2OUT = 0x10;\
  P3DIR = 0xf1;\
  P3OUT = 0x00;\
  P4DIR = 0xfd;\
  P4OUT = ~0x02;\
  P4REN = 0x02;\
  P5DIR = 0xff;\
  P5OUT = 0xff;\
  P6DIR = 0xff;\
  P6OUT = 0x00;

//Radio CS is P4.2
#define SETSS P4OUT|=BIT2
#define CLRSS P4OUT&=~BIT2
#define DIRSS P4DIR|=BIT2

//Flash CS is P4.4, redefine only for the SPI app.
#ifdef SPIAPPLICATION
#undef SETSS
#undef CLRSS
#undef DIRSS
#define SETSS P4OUT|=BIT4
#define CLRSS P4OUT&=~BIT4
#define DIRSS P4DIR|=BIT4
#endif

//CC2420 Chip Enable
#define SETCE P4OUT|=BIT6
#define CLRCE P4OUT&=~BIT6
#define DIRCE P4DIR|=BIT6

//CC2420 signals
#define SFD   (P4IN&BIT1) //Might be broken on the Z1.
#define FIFOP (P1IN&BIT2) // Was 1.0, mistakenly.
#define FIFO  (P1IN&BIT3)


// network byte order converters
#define htons(x) ((((uint16_t)(x) & 0xFF00) >> 8) | \
				 (((uint16_t)(x) & 0x00FF) << 8))
#define htonl(x) ((((uint32_t)(x) & 0xFF000000) >> 24) | \
				  (((uint32_t)(x) & 0x00FF0000) >> 8) | \
				  (((uint32_t)(x) & 0x0000FF00) << 8) | \
				  (((uint32_t)(x) & 0x000000FF) << 24))

#define ntohs htons
#define ntohl htonl

