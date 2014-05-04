/*! 
  \file jtagxscale.c
  \author Dave Huseby <dave@linuxprogrammer.org>
  \brief Intel XScale JTAG
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"
#include "jtagxscale.h"

#define JTAGXSCALE_APP

/* Handles XScale JTAG commands.  Forwards others to JTAG. */
void jtag_xscale_handle_fn( uint8_t const app,
							uint8_t const verb,
							uint32_t const len);

// define the jtag xscale app's app_t
app_t const jtagxscale_app = {

	/* app number */
	JTAGXSCALE,

	/* handle fn */
	jtag_xscale_handle_fn,

	/* name */
	"JTAG XScale",

	/* desc */
	"\tThe JTAG Xscale app extends the JTAG app adding support\n"
	"\tfor JTAG'ing Intel XScale devices.\n"
};


/* From the Intel XScale Core Developer's Manual:
 *
 * The Intel XScale® core provides test features compatible with IEEE Standard
 * Test Access Port and Boundary Scan Architecture (IEEE Std. 1149.1). These 
 * features include a TAP controller, a 5 or 7 bit instruction register, and 
 * test data registers to support software debug. The size of the instruction 
 * register depends on which variant of the Intel XScale® core is being used.
 * This can be found out by examining the CoreGen field of Coprocessor 15, ID 
 * Register (bits 15:13). (See Table 7-4, "ID Register" on page 7-81 for more 
 * details.) A CoreGen value of 0x1 means the JTAG instruction register size 
 * is 5 bits and a CoreGen value of 0x2 means the JTAG instruction register 
 * size is 7 bits.
 *
 */

/* NOTE: I heavily cribbed from the ARM7TDMI jtag implementation. Credit where
 * credit is due. */

void jtag_xscale_reset_cpu(void)
{
	SETRST;
	msdelay(100);
	CLRRST;
	msdelay(100);
	SETRST;
	msdelay(100);
}

/* Handles XScale JTAG commands.  Forwards others to JTAG. */
void jtag_xscale_handle_fn( uint8_t const app,
							uint8_t const verb,
							uint32_t const len)
{	 
	switch(verb) 
	{
	case SETUP:
		/* set up the pin I/O for JTAG */
		jtag_setup();
		/* reset to run-test-idle state */
		jtag_reset_tap();
		/* send back OK */
		txdata(app, verb, 0);
		break;

	case START:
		txdata(app, verb, 0);
		break;

	case STOP:
		txdata(app, verb, 0);
		break;

	case PEEK:
	case POKE:
	case READ:
	case WRITE:
		/* send back OK */
		txdata(app, verb, 0);
		break;

	case JTAG_RESET_TARGET:
		jtag_xscale_reset_cpu();
		txdata(app, verb, 0);
		break;

	default:
		(*(jtag_app.handle))(app,verb,len);
		break;
	}
}
