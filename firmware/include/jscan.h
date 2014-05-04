/*! \file jscan.h
  \author Don A. Bailey
  \brief JSCAN App
*/

#ifndef JSCAN_H
#define JSCAN_H

#include "spi.h"
#include "app.h"

/* app id 'd' */
#define JSCAN 0x64

/* limits */
#define JSCAN_LIMIT_PINS	254
#define JSCAN_DEFAULT_DELAY	1

/* endianness */
#define JSCAN_ENDIAN_BIG	0
#define JSCAN_ENDIAN_LITTLE	1

/* commands */
#define JSCAN_CMD		0x80
#define JSCAN_CMD_SCAN 		(JSCAN_CMD + 0)
#define JSCAN_CMD_ENDIAN	(JSCAN_CMD + 1)
#define JSCAN_CMD_SYNC		(JSCAN_CMD + 2)
#define JSCAN_CMD_ADDPIN	(JSCAN_CMD + 3)
#define JSCAN_CMD_RMPIN		(JSCAN_CMD + 4)
#define JSCAN_CMD_DELAY		(JSCAN_CMD + 5)
#define JSCAN_CMD_PULLUP	(JSCAN_CMD + 6)
#define JSCAN_CMD_LOOPBACK	(JSCAN_CMD + 7)
#define JSCAN_CMD_LISTPIN	(JSCAN_CMD + 8)
#define JSCAN_CMD_RESULTS	(JSCAN_CMD + 9)

extern app_t const jscan_app;

#endif 

