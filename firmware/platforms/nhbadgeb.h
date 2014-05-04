/*! \file nhbadge.h
  \author Travis Goodspeed
  \brief Port descriptions for the Next Hope Badge.
*/


#ifdef MSP430
#include <msp430.h>
#endif

//This nonsense is deprecated.
//Remove as soon as is convenient.
#define P5OUT P4OUT
#define P5DIR P4DIR
#define P5IN P4IN
#define P5REN P4REN

#define SPIOUT P4OUT
#define SPIDIR P4DIR
#define SPIIN  P4IN
#define SPIREN P4REN



//LED on P1.0
#define PLEDOUT P1OUT
#define PLEDDIR P1DIR
#define PLEDPIN BIT0

#define SETSS P4OUT|=BIT4
#define CLRSS P4OUT&=~BIT4
#define DIRSS P4DIR|=BIT4;

//BIT5 is Chip Enable
//#define RADIOACTIVE  P4OUT|=BIT5
//#define RADIOPASSIVE P4OUT&=~BIT5
#define SETCE P4OUT|=BIT5
#define CLRCE P4OUT&=~BIT5
#define DIRCE P4DIR|=BIT5

// network byte order converters
#define htons(x) ((((uint16_t)(x) & 0xFF00) >> 8) | \
				 (((uint16_t)(x) & 0x00FF) << 8))
#define htonl(x) ((((uint32_t)(x) & 0xFF000000) >> 24) | \
				  (((uint32_t)(x) & 0x00FF0000) >> 8) | \
				  (((uint32_t)(x) & 0x0000FF00) << 8) | \
				  (((uint32_t)(x) & 0x000000FF) << 24))

#define ntohs htons
#define ntohl htonl
