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

#include "bl.h"

typedef struct Command Command;

struct
Command
{
	uint8_t t;
	uint8_t s;
	uint16_t l;
	uint8_t v[SPM_PAGESIZE];
};

/* XXX NOTE: 
 * Due to issues with the way avr-gcc interprets named sections, all
 * named section code must be placed in the same file. If placed
 * separately, the section attribute will only effect the last object
 * file with code placed in said section.
 * This can probably be handled with linker scripts, but since the
 * code needs to be sufficiently small, it's just easier to place it
 * all in one namespace.
 *
 * Also, note that data (like strings) apparently can't be placed in
 * a named section and are forced into .data. As a result, we can't
 * use static strings in our code and must instead use chars.
 */

static void bl_fini(void);
static void bl_init(void);
static int bl_command(void);
static int bl_send(Command * );
static int bl_recv(Command * );
static void bl_flash(uint32_t, Command * );
static void bl_peek(uint32_t, Command * );

static void ivt_fini(void);
static void ivt_init(void);

static void usart0_init(void);
static uint8_t usart0_recv(void);
static void usart0_send(uint8_t x);
static uint8_t usart0_srecv(uint8_t, int);

static void xdelay_ms(double);
static void xdelay_loop_2(uint16_t);

static void getsig(uint8_t * );
static void getfuse(uint8_t * );

int
main(void)
{
	void (*app)(void);
	uint8_t x;
	int r;

	bl_init();

	/* NB */
	/* we MUST send at least one byte. there is a bug in some AVR where the USART
	 * will not correctly receive bytes until it has sent at least one byte. Why?
	 * no idea. But, this is the compensating code.
	 */
	x = usart0_srecv('+', 1);

	/* if command mode is requested, enter it. otherwise, drop to the app */
	r = True;
	if(x == '?')
		bl_command();

	/* always exit cleanly */
	bl_fini();

	if(!r)
	{
		/* panic to return to the BLS by triggering the watchdog */
		while(1)
			;
		/* not reached */
	}

	/* execute page zero */
	app = NULL;
	app();

	/* not reached */
	return 0;
}

static int
bl_send(Command * c)
{
	uint16_t i;

	/* respond with a status byte */
	usart0_send(c->s);

	/* send the length in Big Endian */
	usart0_send(c->l >> 8);
	usart0_send(c->l & 0xff);

	/* send the payload */
	for(i = 0; i < c->l; i++)
		usart0_send(c->v[i]);

	return True;
}

static int
bl_recv(Command * c)
{
	uint16_t i;

	/* command byte */
	c->t = usart0_recv();

	/* length in Big Endian */
	c->l = usart0_recv();
	c->l <<= 8;
	c->l |= usart0_recv();

	/* value payload */
	for(i = 0; i < c->l; i++)
		c->v[i] = usart0_recv();

	return True;
}

static int
bl_command(void)
{
	uint32_t a;
	Command c;

	a = 0;
	c.t = 0;

	/* parse commands until exit is requested */
	do
	{
		/* since the user requested to enter the BLS main loop, wait forever */
		if(!bl_recv(&c))
			continue;

		switch(c.t)
		{
		case BL_CMD_PEEK:
			bl_peek(a, &c);
			break;
		case BL_CMD_SETADDR:
			/* address comes in big endian */
			a = c.v[0];
			a <<= 8;
			a |= c.v[1];
			a <<= 8;
			a |= c.v[2];
			a <<= 8;
			a |= c.v[3];

			/* validate the address fits within the application section for this chip */
			c.s = IS_APPSPACE(a) ? BL_ERR_OK : BL_ERR_INVALID;

			/* return the address */
			c.l = 4;
			c.v[0] = a >> 24;
			c.v[1] = a >> 16;
			c.v[2] = a >>  8;
			c.v[3] = a >>  0;

			bl_send(&c);
			break;
		case BL_CMD_FLASH:
			bl_flash(a, &c);
			break;
		case BL_CMD_PAGESZ:
			/* send the total BYTES of the page for this arch */
			c.s = BL_ERR_OK;
			c.l = 2;
			c.v[0] = SPM_PAGESIZE >> 8;
			c.v[1] = SPM_PAGESIZE & 0xff;
			bl_send(&c);
			break;
		case BL_CMD_SIG:
		case BL_CMD_FUSE:
			if(c.t == BL_CMD_SIG)
				getsig(&c.v[0]);
			else
				getfuse(&c.v[0]);
			c.s = BL_ERR_OK;
			c.l = 4;
			bl_send(&c);
			break;
		case BL_CMD_EXIT:
		default:
			c.s = (c.t == BL_CMD_EXIT) ? BL_ERR_OK : BL_ERR_UNIMP;
			c.l = 0;
			bl_send(&c);
			break;
		}
	}
	while(c.t != BL_CMD_EXIT);

	/* NB */
	/* there is currently no way to indicate a critical state error */
	return True;
}

#include "lib/chip.c"

