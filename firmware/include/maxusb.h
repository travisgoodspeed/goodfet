#include "spi.h"


#define MAXUSB 0x40
#define MAXUSB_H

//! Handles a monitor command.
void maxusb_handle_fn( uint8_t const app,
		       uint8_t const verb,
		       uint32_t const len);

extern app_t const maxusb_app;


