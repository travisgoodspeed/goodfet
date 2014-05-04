/*! \file jscan.c
  \author Don A. Bailey
  \brief JTAG Scanner
*/

/* set tabstop=8 */

#include "platform.h"
#include "command.h"

#if (platform != donbfet)
# include <signal.h>
# include <msp430.h>
# include <iomacros.h>
#endif

#include "jscan.h"

#define OFFSETIO 32
#define NPATTERN 64

typedef struct Pin Pin;

struct
Pin
{
	Pin * next;
	Pin * prev;
	uint8_t id;
	uint8_t bit;
	uint8_t pullup;
	volatile uint8_t * ddr;
	volatile uint8_t * pin;
	volatile uint8_t * port;
};

static Pin * pins;
static int nfound;
static uint8_t found[CMDDATALEN];
static char * tap_shiftir = "1111101100";
static uint8_t xdelay = JSCAN_DEFAULT_DELAY;
static uint8_t endian = JSCAN_ENDIAN_LITTLE;
static char pattern[NPATTERN] = "0110011101001101101000010111001001";

static void jscan(uint8_t, uint8_t, uint32_t);

static uint8_t setdelay(uint32_t);
static uint8_t setpullup(uint32_t);
static uint8_t setendian(uint32_t);

static uint8_t npins(void);
static void listpin(uint8_t);
static uint8_t addpin(Pin * );
static uint8_t rmpin(uint32_t);
static uint8_t newpin(uint32_t);
static uint8_t findpin(uint8_t, Pin ** );

static void scan(uint8_t);
static void loopback(uint8_t);
static void getresults(uint8_t);
static void clockstrobe(Pin * );
static void tdipulse(Pin *, Pin *, uint8_t);
static void tapstate(char *, Pin *, Pin * );
static void initpins(Pin *, Pin *, Pin *, Pin *, Pin * );
static int checkdata(char *, int, Pin *, Pin *, Pin *, int * );

app_t const 
jscan_app = 
{
	JSCAN,
	jscan,
	"JSCAN",
	"\tThe JScan app adds support for JTAG brute-force scanning.\n"
};

static void 
jscan(uint8_t a, uint8_t v, uint32_t l)
{
	switch(v)
	{
	case JSCAN_CMD_ADDPIN:
		txdata(a, newpin(l), 1);
		break;
	case JSCAN_CMD_RMPIN:
		txdata(a, rmpin(l), 1);
		break;
	case JSCAN_CMD_DELAY:
		txdata(a, setdelay(l), 1);
		break;
	case JSCAN_CMD_PULLUP:
		txdata(a, setpullup(l), 0);
		break;
	case JSCAN_CMD_LOOPBACK:
		loopback(a);
		break;
	case JSCAN_CMD_ENDIAN:
		txdata(a, setendian(l), 1);
		break;
	case JSCAN_CMD_SCAN:
		scan(a);
		break;
	case JSCAN_CMD_LISTPIN:
		listpin(a);
		break;
	case JSCAN_CMD_RESULTS:
		getresults(a);
		break;
	default:
		debugstr("Verb unimplemented in JSCAN application.");
		txdata(a, NOK, 0);
		break;
	}
}

static uint8_t
npins(void)
{
	uint8_t x;
	Pin * p;

	x = 0;
	p = pins;
	while(p)
	{
		p = p->next;
		x++;
	}

	return x;
}

static uint8_t
newpin(uint32_t l)
{
	Pin * p;

	if(l != 5)
		return NOK;

	if(npins() == JSCAN_LIMIT_PINS)
	{
		return LIMIT;
	}

	if(findpin(cmddata[0], NULL))
	{
		return EXIST;
	}

	p = calloc(1, sizeof *p);
	if(!p)
		return NMEM;

	/* enable pullups by default */
	p->pullup	= 1;

	p->id 		= cmddata[0];
	p->bit		= cmddata[1];
	p->ddr		= (volatile uint8_t * )((uint16_t)cmddata[2] + OFFSETIO);
	p->pin		= (volatile uint8_t * )((uint16_t)cmddata[3] + OFFSETIO);
	p->port		= (volatile uint8_t * )((uint16_t)cmddata[4] + OFFSETIO);

	/* explicitly set return value */
	cmddata[0] = p->id;

	return addpin(p);
}

static uint8_t
addpin(Pin * p)
{
	Pin * a;

	if(!pins)
	{
		pins = p;
		return OK;
	}

	a = pins;
	while(a && a->next)
		a = a->next;
	a->next = p;
	p->prev = a;

	return OK;
}

static uint8_t
rmpin(uint32_t l)
{
	uint8_t i;
	Pin * p;

	if(l != 1)
		return NOK;

	i = cmddata[0];
	if(!findpin(i, &p))
		return NOK;

	if(p->prev)
		(p->prev)->next = p->next;
	if(p->next)
		(p->next)->prev = p->prev;
	if(p == pins)
		pins = p->next;

	free(p);

	cmddata[0] = i;

	return OK;
}

static uint8_t 
findpin(uint8_t i, Pin ** pp)
{
	Pin * p;

	p = pins;
	while(p)
	{
		if(p->id == i)
		{
			if(pp)
				*pp = p;
			return 1;
		}

		p = p->next;
	}

	return 0;
}

static uint8_t
setdelay(uint32_t l)
{
	if(l != 1)
	{
		cmddata[0] = xdelay;
		return OK;
	}

	xdelay = cmddata[0];
	return OK;
}

static uint8_t
setpullup(uint32_t l)
{
	Pin * p;

	if(l != 2)
		return NOK;

	/* change all or one? */
	if(cmddata[0] != 0xff)
	{
		if(!findpin(l, &p))
			return EXIST;
		p->pullup = cmddata[1] ? 1 : 0 ;
	}
	else
	{
		p = pins; 
		while(p)
		{
			p->pullup = cmddata[1] ? 1 : 0 ;
			p = p->next;
		}
	}

	return OK;
}

static uint8_t
setendian(uint32_t l)
{
	if(l != 1)
	{
		cmddata[0] = endian;
		return OK;
	}

	switch(cmddata[0])
	{
	case JSCAN_ENDIAN_BIG:
		endian = JSCAN_ENDIAN_BIG;
		break;
	case JSCAN_ENDIAN_LITTLE:
		endian = JSCAN_ENDIAN_LITTLE;
		break;
	default:
		return NOK;
	}

	return OK;
}

static void
loopback(uint8_t a)
{
	Pin * tdo;
	Pin * tdi;
	int nb;
	int r;

	if(npins() < 2)
	{
		txdata(a, EXIST, 0);
		return;
	}

	nb = 0;

	tdo = pins;
	while(tdo)
	{
		tdi = pins;
		while(tdi)
		{
			if(tdi == tdo)
			{
				tdi = tdi->next;
				continue;
			}

			initpins(NULL, NULL, tdi, NULL, NULL);

			r = checkdata(pattern, (2*NPATTERN), NULL, tdi, tdo, NULL);
			if(r == 1)
			{
				if(nb >= (CMDDATALEN-4))
				{
					txdata(a, NMEM, 0);
					return;
				}

				/* add the response in couples; TDI first */
				cmddata[nb++] = tdi->id;
				cmddata[nb++] = tdo->id;
			}

			tdi = tdi->next;
		}

		tdo = tdo->next;
	}

	txdata(a, OK, nb);
}

static void
initpins(Pin * tck, Pin * tms, Pin * tdi, Pin * tdo, Pin * nrst)
{
	Pin * p;

/* XXX test removing syncs */
	p = pins;
	while(p)
	{
		/* set as input by default */
		*p->ddr &= ~(1 << p->bit);

		/* sync */
		_delay_ms(xdelay);

		/* set pullup if desired while in input mode */
		if(p->pullup)
			*p->port |= (1 << p->bit);
		else
			*p->port &= ~(1 << p->bit);

		/* sync */
		_delay_ms(xdelay);

		if(p == nrst)
		{
			/* set as output */
			*p->ddr |= (1 << p->bit);

			/* nrst requires output fixed high */
			*p->port &= ~(1 << p->bit);
			*p->port |=  (1 << p->bit);
		}
		else if(p == tck || p == tms || p == tdi)
		{
			/* set as output */
			*p->ddr |= (1 << p->bit);

			/* sync */
			_delay_ms(xdelay);

			/* these pins must start low */
			*p->port &= ~(1 << p->bit);
		}

		/* tdo should need no special sauce */

		/* sync */
		_delay_ms(xdelay);

		p = p->next;
	}
}

static int
checkdata(char * pattern, int ntimes, Pin * tck, Pin * tdi, Pin * tdo, int * nreg)
{
        char rcv[NPATTERN];
        int tdo_read;
        int tdo_prev;
        int ntoggle;
        uint8_t x;
        int np;
        int i;
        int w;

        w = 0;
        np = strlen(pattern);

        x = (*tdo->pin & (1 << tdo->bit)) >> tdo->bit;

        tdo_prev = '0' + (x == 1);

        for(i = 0; i < ntimes; i++)
        {
                tdipulse(tck, tdi, pattern[w++] - '0');
                if(!pattern[w])
                {
                        w = 0;
                }

                x = (*tdo->pin & (1 << tdo->bit)) >> tdo->bit;

                tdo_read = '0' + (x == 1);

                ntoggle += (tdo_read != tdo_prev);
                tdo_prev = tdo_read;

                if(i < np)
                {
                        rcv[i] = tdo_read;
                }
                else
                {
                        memmove(rcv, rcv + 1, np - 1);
                        rcv[np - 1] = tdo_read;
                }

                if(i >= np - 1)
                {
                        if(!memcmp(pattern, rcv, np))
                        {
                                if(nreg)
                                        *nreg = i + 1 - np;
                                return 1;
                        }
                }
        }

        if(nreg)
                *nreg = 0;

        return ntoggle > 1 ? ntoggle : 0 ;
}

static void
tdipulse(Pin * tck, Pin * tdi, uint8_t x)
{
	if(x)   
		*tdi->port |= (1 << tdi->bit);
	else
		*tdi->port &= ~(1 << tdi->bit);

	/* sync */
	_delay_ms(xdelay);

	clockstrobe(tck);
}

static void
clockstrobe(Pin * tck)
{
	*tck->port |= (1 << tck->bit);
	_delay_ms(xdelay);

	*tck->port &= ~(1 << tck->bit);
	_delay_ms(xdelay);
}

static void
scan(uint8_t a)
{
	Pin * nrst;
	Pin * tck;
	Pin * tms;
	Pin * tdi;
	Pin * tdo;
	int nreg;
	int r;

        if(npins() < 5)
        {
                txdata(a, EXIST, 0);
                return;
        }

	nfound = 0;
        nrst = pins;

	/* send back an OK to let the user know we've started */
	txdata(a, OK, 0);

        while(nrst)
        {
                tck = pins;
                while(tck)
                {
                        if(tck == nrst)
                        {
                                tck = tck->next;
                                continue;
                        }

                        tms = pins;
                        while(tms)
                        {
                                if(tms == nrst || tms == tck)
                                {
                                        tms = tms->next;
                                        continue;
                                }

                                tdo = pins;
                                while(tdo)
                                {
                                        if(tdo == nrst || tdo == tck || tdo == tms)
                                        {
                                                tdo = tdo->next;
                                                continue;
                                        }

                                        tdi = pins;
                                        while(tdi)
                                        {
                                                if(tdi == nrst || tdi == tck || tdi == tms || tdi == tdo)
                                                {
                                                        tdi = tdi->next;
                                                        continue;
                                                }

                                                initpins(tck, tms, tdi, tdo, nrst);

                                                tapstate(tap_shiftir, tck, tms);

                                                r = checkdata(pattern, (2*NPATTERN), tck, tdi, tdo, &nreg);
                                                if(r == 1)
                                                {
							/* found potential JTAG */
							/* NB */
							/* can fit around 100 detections; but total should hover around 0.5% of total tests. 
							 * so if the number of tests is really high, one could exceed 100 detected JTAGs,
							 * so caveat emptor
							 */
							if(nfound < (CMDDATALEN-4)-5)
							{
								/* order is important */
								found[nfound++] = tck->id;
								found[nfound++] = tms->id;
								found[nfound++] = tdi->id;
								found[nfound++] = tdo->id;
								found[nfound++] = nrst->id;
							}
                                                }

						tdi = tdi->next;
                                        }

                                        tdo = tdo->next;
                                }

                                tms = tms->next;
                        }

                        tck = tck->next;
                }

                nrst = nrst->next;
        }

}

static void
tapstate(char * s, Pin * tck, Pin * tms)
{
        int x;

        while(*s)
        {
                x = *s - '0';
                /* issue */
                if(x)   
                        *tms->port |= (1 << tms->bit);
                else
                        *tms->port &= ~(1 << tms->bit);

                /* strobe */
                *tck->port &= ~(1 << tck->bit);
                _delay_ms(xdelay);
                *tck->port |= (1 << tck->bit);

                s++;
        }
}

static void
listpin(uint8_t a)
{
	Pin * p;
	int nb;

	nb = 0;
	p = pins;
	while(p)
	{
		cmddata[nb++] = p->id;
		cmddata[nb++] = p->bit;
		cmddata[nb++] = ((uint16_t)(p->ddr)) & 0xff;
		cmddata[nb++] = ((uint16_t)(p->pin)) & 0xff;
		cmddata[nb++] = ((uint16_t)(p->port)) & 0xff;
		p = p->next;
	}

	txdata(a, OK, nb);
}

static void
getresults(uint8_t a)
{
	memcpy(cmddata, found, nfound);
	txdata(a, OK, nfound);
}

