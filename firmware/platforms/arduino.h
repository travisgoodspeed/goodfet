/*! \file goodfet.h
  \author Travis Goodspeed
  \brief Port descriptions for the GoodFET platform.
*/

#define ARDUINO

#define F_CPU 8000000UL

void arduino_init();

#include <avr/io.h>
//#include <util/delay.h>

//LED on P1.0
#define PLEDOUT PORTB
#define PLEDDIR DDRB
#define PLEDPIN 0x20

//Use P3 instead of P5 for target I/O on chips without P5.
#ifdef msp430f2274
//#warning "No P5, using P3 instead.  Will break 2618 and 1612 support."
#define P5OUT P3OUT
#define P5DIR P3DIR
#define P5IN P3IN
#define P5REN P3REN

#define SPIOUT P3OUT
#define SPIDIR P3DIR
#define SPIIN  P3IN
#define SPIREN P3REN
#else

#define SPIOUT P5OUT
#define SPIDIR P5DIR
#define SPIIN  P5IN
#define SPIREN P5REN

#endif

//This is how things used to work, don't do it anymore.
//#ifdef msp430x1612
//#define P5REN somedamnedextern
//#endif

//No longer works for Hope badge.
#define SETSS P5OUT|=BIT0
#define CLRSS P5OUT&=~BIT0
#define DIRSS P5DIR|=BIT0;

//Used for the Nordic port, !RST pin on regular GoodFET.
#define SETCE P2OUT|=BIT6
#define CLRCE P2OUT&=~BIT6
#define DIRCE P2DIR|=BIT6

// network byte order converters
#define htons(x) ((((uint16_t)(x) & 0xFF00) >> 8) | \
				 (((uint16_t)(x) & 0x00FF) << 8))
#define htonl(x) ((((uint32_t)(x) & 0xFF000000) >> 24) | \
				  (((uint32_t)(x) & 0x00FF0000) >> 8) | \
				  (((uint32_t)(x) & 0x0000FF00) << 8) | \
				  (((uint32_t)(x) & 0x000000FF) << 24))

#define ntohs htons
#define ntohl htonl

