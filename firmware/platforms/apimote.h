/*! \file apimote.h
  \author Ryan Speers
  \brief Port descriptions for the Apimote platform.
*/

#ifndef _GNU_ASSEMBLER_
#include <msp430.h>
#endif

//LED on P5.5 (pin 49) (LED1 red)
#define PLEDOUT P5OUT
#define PLEDDIR P5DIR
#define PLEDPIN BIT5
//LED on P5.6 (pin 50) (LED2 green)
#define PLED2OUT P5OUT
#define PLED2DIR P5DIR
#define PLED2PIN BIT6
//LED on P5.7 (pin 51) (LED3 blue)
#define PLED3OUT P5OUT
#define PLED3DIR P5DIR
#define PLED3PIN BIT7

//SPI
//TelosB:  29/3.1=RF_SI, 30/3.2=RF_SO, 31/3.3=RF_SCLK
//ApiMote: 29/3.1=RF_SI, 30/3.2=RF_SO, 31/3.3=RF_SCLK
#define SPIOUT P3OUT
#define SPIDIR P3DIR
#define SPIIN  P3IN
#define SPIREN P3REN

/* For the radio to be used:
   2.7 (!RST) must be low
   2.0 (VREF_EN) must be high (cc2420-41 rf_vreg)
   3.0 (!CS) must be low for the transaction.
*/

/* INITPLATFORM         PX.7  PX.6  PX.5  PX.4  PX.3  PX.2  PX.1  PX.0
                        EXP_USR NC  EINT5 EINT4 EINT3 EINT2 MTXFRX EINT1
  P1DIR = 0xff 11111111 In          In    In    In    In    Out    In
  P1OUT = 0x00                                              Lo
  P1IE  = 0xbd 10111101 Int         Int   Int   Int   Int          Int
  P1IE @ 025h (UGpg341)                                     ^BSLTX

                        R_RST R_SFD RGIO1 R_PKT RGIO0 MRXFTX G_RST R_VREG
  P2DIR = 0x83 10000011 Out   In    In    In    In    In     Out   Out
  P2OUT = 0x81 10000001 Hi    Lo                             Lo?   Hi
                                                      ^BSLRX

                        MRXFTXMTXFRX G_RX G_TX  RSCLK R_SO  R_SI  RF_CSn
  P3DIR = 0x5b 01011011 In    Out    In   Out   Out   In    Out?  Out
  P3OUT = 0x            Lo    Lo     Lo?  Lo?   Lo    Lo    Lo    Hi
  P3SEL = 0xff 11111111 Pri   Pri    Pri  Pri   Pri   Pri   Pri   Pri 
  P3SEL2= 0x00 
  (SEL2=0,SEL=1: Primary Peripheral Func; 1,1: Secondary Peripheral)
 
                        G_TST NC    F_CSn FHold R_ANT NC    NC    NC
  P4DIR = 0xff 11111111 Out         Out   Out   Out   
  P4OUT = 0x30 00110000 Lo?         Hi    Hi    Lo

                        LED3  LED2  LED1  NC    GSCLK G_SD  G_SI  G_CSn
  P5DIR = 0xfb 11111011 Out   Out   Out         Out   In    Out   Out
  P5OUT = 0x80 10000000 Hi    Hi    Hi          Lo?         Lo?   Lo?

                        ADC5  ADC4  ADC3  ADC2  ADC1  NC    BADC2 BADC1
  P6DIR = 0xc7 11000111 Out   Out   In    In    In          Out   Out
  P6OUT = 0x00          Lo    Lo                            Lo    Lo
*/

#define INITPLATFORM \
  P2DIR |= BIT0+BIT7; \
  P2OUT &= ~BIT7; \
  P2OUT |= BIT0; \
  P3DIR |= BIT0;

  /*
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
  */


//RF Control
//TelosB:  Radio CS is 38/P4.2 (to CC2420 pin31)
//ApiMote: Radio CS is 28/P3.0
#define SETSS P3OUT|=BIT0
#define CLRSS P3OUT&=~BIT0
#define DIRSS P3DIR|=BIT0

//CC2420 Chip Enable
//TelosB:  Radio RESETn is 42/P4.6 (to CC2420 pin21)
//ApiMote: Radio RESETn is 27/P2.7 (to CC2420 pin21)
#define SETCE P2OUT|=BIT7
#define CLRCE P2OUT&=~BIT7
#define DIRCE P2DIR|=BIT7

//CC2420 signals
#define SFD   (P2IN&BIT6) //TelosB 37/P4.1 -> ApiMote 26/P2.6
#define FIFOP (P2IN&BIT4) //TelosB 12/P1.0 -> ApiMote 24/P2.4 (rf_pkt cc2420-29)
#define FIFO  (P2IN&BIT3) //TelosB 15/P1.3 -> ApiMote 23/P2.3 (rf_gio0 cc2420-30)

// network byte order converters
#define htons(x) ((((uint16_t)(x) & 0xFF00) >> 8) | \
				 (((uint16_t)(x) & 0x00FF) << 8))
#define htonl(x) ((((uint32_t)(x) & 0xFF000000) >> 24) | \
				  (((uint32_t)(x) & 0x00FF0000) >> 8) | \
				  (((uint32_t)(x) & 0x0000FF00) << 8) | \
				  (((uint32_t)(x) & 0x000000FF) << 24))

#define ntohs htons
#define ntohl htonl

