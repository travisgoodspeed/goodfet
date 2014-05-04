/*! \file telosb.h
  \author Travis Goodspeed
  \brief Port descriptions for the TelosB platform.
  
  This file defines the Telos B hardware, so that the GoodFET firmware
  may be loaded onto it.  Adjustments include the !CS line of the CC2420
  radio, the choice of serial port, and the LEDs.

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

/* INITPLATFORM         PX.7  PX.6  PX.5  PX.4  PX.3  PX.2  PX.1  PX.0
                        HUM   HUM   HUM   RGIO1 RGIO0 PDVCC UART1TX PKT_INT
  P1DIR = 0xe0 11100000 Out   Out   Out   In    In    In    In    In
  P1OUT = 0x00                                              Out??
                        UsrInt GIO3 NC    1Wire GIO2 UART1RX GIO1 GIO0
  P2DIR = 0x7b 01111011 In    Out   Out   Out   Out   In    Out   Out
  P2OUT = 0x10 00010000                   Hi
                        U1RX  U1TX  U0RX  U0TX  RSCLK R_SO  R_SI  NC
  P3DIR = 0xf1 11110001 Out   Out   Out   Out   In    In    In    Out
  P3OUT = 0x00
                        FHold RRST RVREFEN F_CS NC    R_CS  R_SFD NC
  P4DIR = 0xfd 11111101 Out   Out   Out   Out   Out   Out   In    Out
  P4OUT = 0xfd 11111101 Hi    Hi    Hi    Hi    Hi    Hi    Lo    Hi
                        SVSoutLED3  LED2  LED1  NC    NC    NC    NC
  P5DIR = 0xff 11111111 Out   Out   Out   Out   Out   Out   Out   Out
  P5OUT = 0xff 11111111 Hi    Hi    Hi    Hi    Hi    Hi    Hi    Hi
                        SVSin DAC0  ADC5  ADC4  ADC3  ADC2  ADC1  ADC0
  P6DIR = 0xff 11111111 Out   Out   Out   Out   Out   Out   Out   Out
  P6OUT = 0x00
*/

/* For the radio to be used:
   4.6 (!RST) must be low
   4.5 (VREF_EN) must be high
   4.2 (!CS) must be low for the transaction.
*/

#define INITPLATFORM \
  P1DIR = 0xe0;\
  P1OUT = 0x00;\
  P2DIR = 0x7b;\
  P2OUT = 0x10;\
  P3DIR = 0xf1;\
  P3OUT = 0x00;\
  P4DIR = 0xfd;\
  P4OUT = 0xFd;\
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
#define SFD   (P4IN&BIT1)
#define FIFOP (P1IN&BIT0)
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

