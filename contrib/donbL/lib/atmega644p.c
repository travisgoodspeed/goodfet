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

/* ATmega644P */
/* This file represents the chip specific routines and macros that
 * should be used in the more generic Boot Loader 
 */

static void
bl_init(void)
{
	/* explicitly clear interrupts */
	cli();

        /* disable the watchdog timer; this macro will disable interrupts for us */
        /* NOTE: ensure that the WDRF flag is unset in the MCUSR or we will spinlock
         * when the watchdog times out
         */
        MCUSR &= ~(1 << WDRF);
        wdt_disable();

	/* move the vectors */
	ivt_init();

	/* init the USART */
        usart0_init();

	/* explicitly enable interrupts */
	sei();
}

static void
bl_fini(void)
{
	/* explicitly clear interrupts */
	cli();

	/* move vectors back to userland */
	ivt_fini();

        /* enable the watchdog timer; this macro will disable interrupts for us */
        /* NOTE: ensure that the WDRF flag is unset in the MCUSR or we will spinlock
         * when the watchdog times out
         */
        MCUSR &= ~(1 << WDRF);
        wdt_enable(WDTO_15MS);

	/* explicitly enable interrupts */
	sei();
}

static void
bl_flash(uint32_t a, Command * c)
{
        uint16_t w;
        int i;

        /* we should now have SPM_PAGESIZE (or less) bytes in the payload 
         * - generate a checksum from this payload and match it to the previously set checksum 
         * - if it matches, flash the page into the last set address
         * - validate the flashed page by generating a checksum from reading it
         * - return BL_ERR_OK to the user if all is well
         */

        /* validate the payload length */
        if(c->l > SPM_PAGESIZE)
        {
                c->s = BL_ERR_INVALID;
                c->l = 0;
                bl_send(c);
                return;
        }

        /* fill the page */
	/* if there aren't enough bytes to complete the page, do it here since we
	 * don't require the client to do it to save the byte transfer over USART
	 */
        for(i = 0; i < (int)c->l || i < SPM_PAGESIZE; i += 2)
        {
                /* data in the payload should mirror the ihex standard, so the
                 * data bytes should be in little endian words (albeit unintentionally)
                 */
		if(i >= (int)c->l)
			w = 0xffff;
		else
                	w = ((c->v[i+1] << 8)|c->v[i]);

                boot_page_fill_safe(a + i, w);
        }

        /* erase the page and wait for the action to complete */
        boot_page_erase_safe(a);

        /* write the page and wait for the action to complete */
        boot_page_write_safe(a);

        /* re-enable RWW section */
        boot_rww_enable_safe();

        /* NB */
        /* now validate the checksum; note that this isn't the checksum 
         * found in the ihex file because we lose some information (record type
         * and some address data) in the upload; so, this is simply a checksum
         * of the payload and that's all
         */
        w = 0;
        for(i = 0; i < (int)c->l; i++)
        {
                /* add each byte */
                w += pgm_read_byte_near(a + i);
        }

        /* twos complement the value */
        w = 0x100 - w;

        /* generate the response; return the checksum so the user can validate */
        c->v[0] = w & 0xff;
        c->s = BL_ERR_OK;
        c->l = 1;

        bl_send(c);
}

static void
bl_peek(uint32_t a, Command * c)
{
	uint16_t w;

	w = pgm_read_word_near(a);

	c->s = BL_ERR_OK;
	c->v[0] = w >> 8;
	c->v[1] = w;
	c->l = 2;

	bl_send(c);
}

static void
usart0_init(void)
{
	/* disable briefly */
        UCSR0B = 0;

        UBRR0L = 4;     /* 500,000 baud at 20MHz */
        UBRR0H = 0;

        UCSR0A = (1 << U2X0);   /* double the baud rate */
        UCSR0C = (3 << UCSZ00); /* 8N1 */

        /* enabling rx/tx must be done after frame/baud setup */
        UCSR0B = ((1 << TXEN0) | (1 << RXEN0));
}

static void
usart0_send(uint8_t x)
{
        loop_until_bit_is_set(UCSR0A, UDRE0);
        UDR0 = x;
}

static uint8_t
usart0_recv(void)
{
	while(!(UCSR0A & (1 << RXC0)))
		;
	return UDR0;
}

static uint8_t
usart0_srecv(uint8_t v, int s)
{
        int r;
	int i;

        /* wait 's' seconds before bailing */
        r = 0;
        while(s--)
        {
		/* send a byte */
		if(v != 0)
			usart0_send(v);

		for(i = 0; i < 100; i++)
		{
			/* wait for the response */
                	r = (UCSR0A & (1 << RXC0)) != 0;
                	if(r)
        			return UDR0;
                	xdelay_ms(10);
		}
        }

        return 0;
}

static void
getfuse(uint8_t * s)
{
        /* read lock bits */
        s[0] = boot_lock_fuse_bits_get(1);

        /* read fuse extended */
        s[1] = boot_lock_fuse_bits_get(2);

        /* read high fuse */
        s[2] = boot_lock_fuse_bits_get(3);

        /* read low fuse */
        s[3] = boot_lock_fuse_bits_get(0);
}

static void
getsig(uint8_t * s)
{
	/* a delay is required otherwise values will be incorrect */
        /* device signature byte 1 */
        s[0] = boot_signature_byte_get(0);
        xdelay_ms(3);

        /* device signature byte 2 */
        s[1] = boot_signature_byte_get(2);
        xdelay_ms(3);

        /* device signature byte 3 */
        s[2] = boot_signature_byte_get(4);
        xdelay_ms(3);

        /* rc oscillator calibration byte */
        s[3] = boot_signature_byte_get(1);
}

static void
xdelay_ms(double __ms)
{
        uint16_t __ticks;
        double __tmp = ((F_CPU) / 4e3) * __ms;
        if (__tmp < 1.0)
                __ticks = 1;
        else if (__tmp > 65535)
        {
                //      __ticks = requested delay in 1/10 ms
                __ticks = (uint16_t) (__ms * 10.0);
                while(__ticks)
                {
                        // wait 1/10 ms
                        xdelay_loop_2(((F_CPU) / 4e3) / 10);
                        __ticks --;
                }
                return;
        }
        else
                __ticks = (uint16_t)__tmp;
        xdelay_loop_2(__ticks);
}

static void
xdelay_loop_2(uint16_t __count)
{
        __asm__ volatile (
                "1: sbiw %0,1" "\n\t"
                "brne 1b"
                : "=w" (__count)
                : "0" (__count)
        );
}

static void
ivt_init(void)
{
        /* enable change of interrupt vectors */
        /* NOTE: setting IVCE disables interrupts until the bit is auto-unset 
         * 4 cycles after being set or after IVSEL is written
         */
        MCUCR |= (1 << IVCE);

        /* move interrupts to boot flash section */
        MCUCR |= (1 << IVSEL);
}

static void
ivt_fini(void)
{
	uint8_t x;

        /* move interrupts from boot flash section */
	/* NB */
	/* you MUST use a variable during this process. even highly optimized,
	 * masking the bit, shifting, ANDing, and setting MCUCR will exceed
	 * 4 CPU cycles! set a variable with the desired value for MCUCR and
	 * then set the register once IVCE is enabled
	 */
        x = MCUCR & ~(1 << IVSEL);

        /* enable change of interrupt vectors */
        /* NOTE: setting IVCE disables interrupts until the bit is auto-unset 
         * 4 cycles after being set or after IVSEL is written
         */
        MCUCR |= (1 << IVCE);
	MCUCR = x;
}

/* NB */
/* this is a huge deal; for some reason vectors in App Land WILL NOT 
 * execute unless a handler is defined in Boot Loader Land!!! as a 
 * result, the BLS will need to define ISRs for each vector that
 * needs to be handled by the Application. Since this is a huge 
 * drain on resources, the Intr API should be moved to BLS so that
 * Apps can register interrupt handlers and the IVTs never need to
 * be moved from NRWW space!
 *
BL_ISR(USART0_RX_vect)
{
	__asm__("reti");
}

BL_ISR(TIMER1_COMPA_vect)
{
	__asm__("reti");
}
 */

