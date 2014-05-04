/*! \file nhbadge.h
  \author Travis Goodspeed
  \brief Port descriptions for the Next Hope Badge.
*/


#ifdef MSP430
#include <msp430.h>
#endif


//LED on P1.0
#define PLEDOUT P1OUT
#define PLEDDIR P1DIR
#define PLEDPIN BIT0


//No longer works for Hope badge.
#define SETSS P5OUT|=BIT4
#define CLRSS P5OUT&=~BIT4
#define DIRSS P5DIR|=BIT4;

//BIT5 is Chip Enable
//#define RADIOACTIVE  P5OUT|=BIT5
//#define RADIOPASSIVE P5OUT&=~BIT5
#define SETCE P5OUT|=BIT5
#define CLRCE P5OUT&=~BIT5
#define DIRCE P5DIR|=BIT5

#define SPIOUT P5OUT
#define SPIDIR P5DIR
#define SPIIN  P5IN
#define SPIREN P5REN

// network byte order converters
#define htons(x) ((((uint16_t)(x) & 0xFF00) >> 8) | \
				 (((uint16_t)(x) & 0x00FF) << 8))
#define htonl(x) ((((uint32_t)(x) & 0xFF000000) >> 24) | \
				  (((uint32_t)(x) & 0x00FF0000) >> 8) | \
				  (((uint32_t)(x) & 0x0000FF00) << 8) | \
				  (((uint32_t)(x) & 0x000000FF) << 24))

#define ntohs htons
#define ntohl htonl
