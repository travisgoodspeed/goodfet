/*! \file donbfet.h
  \author Don A. Bailey
  \brief Port descriptions for the DonbFET platform.
*/

/* NB: define default CPU frequency */
//XXX #define F_CPU 8000000UL
#define F_CPU 20000000UL

#include <avr/io.h>
#include <avr/wdt.h>
#include <avr/boot.h>
#include <avr/sleep.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <util/delay.h>
#include <inttypes.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>
#include <stdio.h>
#include <ctype.h>

/* all AVR SRAM starts after I/O mapped memory and registers */
#define RAMSTART 0x100

#ifndef PB0
# define PB0 PORTB0
#endif
#ifndef PA0
# define PA0 PORTA0
#endif
#ifndef PA1
# define PA1 PORTA1
#endif
#ifndef PA2
# define PA2 PORTA2
#endif
#ifndef PA3
# define PA3 PORTA3
#endif
#ifndef PA4
# define PA4 PORTA4
#endif
#ifndef PA5
# define PA5 PORTA5
#endif

//LED on P1.0
#define PLEDOUT PORTB
#define PLEDDIR DDRB
#define PLEDPIN PB0

//Use P3 instead of P5 for target I/O on chips without P5.
#ifdef msp430f2274
//#warning "No P5, using P3 instead.  Will break 2618 and 1612 support."
# define P5OUT P3OUT
# define P5DIR P3DIR
# define P5IN P3IN
# define P5REN P3REN

# define SPIOUT P3OUT
# define SPIDIR P3DIR
# define SPIIN  P3IN
# define SPIREN P3REN
#else

# if (platform == donbfet)
#  define SPIOUT PORTA
#  define SPIDIR DDRA
#  define SPIIN  PINA
//# define SPIREN P5REN
# endif
#endif

//This is how things used to work, don't do it anymore.
//#ifdef msp430x1612
//#define P5REN somedamnedextern
//#endif

#if (platform == donbfet)
# define SETSS PORTA|=SS;
# define CLRSS PORTA&=~SS;
# define DIRSS DDRA|=SS;
#else
//No longer works for Hope badge.
# define SETSS P5OUT|=BIT0
# define CLRSS P5OUT&=~BIT0
# define DIRSS P5DIR|=BIT0;
#endif

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

extern uint8_t donbfet_get_byte(uint16_t);

