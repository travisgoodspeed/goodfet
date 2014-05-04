/*! \file ejtag.c
  \author Travis Goodspeed <travis at radiantmachines.com>
  \brief MIPS EJTAG (32-bit)
*/

#include "platform.h"
#include "command.h"
#include "jtag.h"
#include "ejtag.h"

//! Handles MIPS EJTAG commands.  Forwards others to JTAG.
void ejtag_handle_fn( uint8_t const app,
					  uint8_t const verb,
					  uint32_t const len);

// define the ejtag app's app_t
app_t const ejtag_app = {

	/* app number */
	EJTAG,

	/* handle fn */
	ejtag_handle_fn,

	/* name */
	"EJTAG",

	/* desc */
	"\tThe EJTAG app extends the basic JTAG app with support\n"
	"\tfor JTAG'ing MIPS based devices.\n"
};

//! Handles MIPS EJTAG commands.  Forwards others to JTAG.
void ejtag_handle_fn( uint8_t const app,
					  uint8_t const verb,
					  uint32_t const len)
{
	switch(verb)
	{
	case START:
		cmddata[0] = jtag_ir_shift_8(EJTAG_IR_BYPASS);
		txdata(app, verb, 1);
		break;
	case STOP:
		txdata(app,verb,0);
		break;
	case PEEK:
		//WRITEME
	case POKE:
		//WRITEME
	default:
		(*(jtag_app.handle))(app, verb, len);
	}
}
