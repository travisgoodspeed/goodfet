/*! \file command.h
  \author Travis Goodspeed
  \brief Command codes and buffers.
*/


#ifndef COMMAND_H
#define COMMAND_H

#include <stdint.h>

//Types
#define u8 unsigned char
#define u16 unsigned int
#define u32 unsigned long


#ifdef msp430f2274
//256 bytes, plus overhead
//For chips with very little RAM.
#define CMDDATALEN 0x104
//#warning Very little RAM.
#endif

#ifndef CMDDATALEN
//512 bytes
#define CMDDATALEN 0x204
//4k
//#define CMDDATALEN 0x1004
#endif

//! Global data buffer.
extern unsigned char cmddata[CMDDATALEN];
extern unsigned char silent;

#define cmddataword ((unsigned int*) cmddata)
#define cmddatalong ((unsigned long*) cmddata)
#define memorybyte ((char*)  0)
//#define memoryword ((unsigned int*)  0))

// Global Commands
#define READ  0x00
#define WRITE 0x01
#define PEEK  0x02
#define POKE  0x03
#define SETUP 0x10
#define START 0x20
#define STOP  0x21
#define CALL  0x30
#define EXEC  0x31
#define LIMIT 0x7B /* limit reached */
#define EXIST 0x7C /* already or doesnt exist */
#define NMEM  0x7D /* OOM */
#define NOK   0x7E
#define OK    0x7F

#define DEBUGSTR 0xFF



//SPI commands
#define SPI_JEDEC 0x80
#define SPI_ERASE 0x81
#define SPI_RW_EM260 0x82
#define SPI_ZENSYS_ENABLE 0x83
#define SPI_ZENSYS_WRITE3_READ1 0x84
#define SPI_ZENSYS_WRITE2_READ2 0x85

//OCT commands
#define OCT_CMP 0x90
#define OCT_RES 0x91

#ifdef GCC
#define WEAKDEF __attribute__ ((weak))
#else
//Compiler doesn't support weak linking. :(
#define WEAKDEF
#endif

//! Handle a command.  Defined in goodfet.c
void handle(uint8_t const app,
			uint8_t const verb,
			uint32_t const len);
//! Transmit a header.
void txhead(unsigned char app,
	    unsigned char verb,
	    unsigned long len);
//! Transmit data.
void txdata(unsigned char app,
	    unsigned char verb,
	    unsigned long len);
//! Transmit a string.
void txstring(unsigned char app,
	      unsigned char verb,
	      const char *str);

//! Receive a long.
unsigned long rxlong();
//! Receive a word.
unsigned int rxword();

//! Transmit a long.
void txlong(unsigned long l);
//! Transmit a word.
void txword(unsigned int l);

//! Transmit a debug sequence of bytes
void debugbytes(const char *bytes, unsigned int len);
//! Transmit a debug string.
void debugstr(const char *str);
//! brief Debug a hex word string.
void debughex(u16 v);
//! brief Debug a hex long string.
void debughex32(u32 v);

//! Delay for a count.
void delay(unsigned int count);
//! MSDelay
void msdelay(unsigned int ms);


//! Prepare Timer B; call before using delay_ms or delay_us.
void prep_timer();

//! Delay for specified number of milliseconds (given 16 MHz clock)
void delay_ms( unsigned int ms );

//! Delay for specified number of microseconds (given 16 MHz clock)
void delay_us( unsigned int us );

//! Delay for specified number of clock ticks (16 MHz clock implies 62.5 ns per tick).
void delay_ticks( unsigned int num_ticks );

#endif // COMMAND_H
