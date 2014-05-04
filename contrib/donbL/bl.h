/*
 * Copyright 2011 Don A. Bailey
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

/* NB: define default CPU frequency */
// XXX #define F_CPU 8000000UL
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

enum
{
        False,
        True
};

#define nil ((void * )0)
#define USED(x) (*(&(x)) = (x))
#define nelem(x) (sizeof(x)/sizeof((x)[0]))

/* generate the base word address from the define macros */
#define BL_WORD_BASE ((BL_BYTE_BASE)/2)

/* valid addresses that can be flashed by the boot loader include 0 through 
 * the end of the last page before the boot loader address
 */
#define IS_APPSPACE(x) ((x) <= (BL_WORD_BASE - (SPM_PAGESIZE/2)))

/* command bytes for the BL command processor */
#define BL_CMD_SIG	0x01
#define BL_CMD_FUSE	0x02
#define BL_CMD_PAGESZ	0x03
#define BL_CMD_FLASH	0x04
#define BL_CMD_SETADDR	0x05
#define BL_CMD_PEEK	0x06
#define BL_CMD_EXIT	0x07

/* command response codes */
#define BL_ERR_OK 	0x00
#define BL_ERR_UNIMP 	0x01
#define BL_ERR_INVALID	0x02
#define BL_ERR_CHECKSUM	0x03

/* XXX */
/* attempt an ISR definition that's naked to limit code size */
#define BL_ISR(vector)            \
    void vector (void) __attribute__ ((naked)) ; \
    void vector (void)

