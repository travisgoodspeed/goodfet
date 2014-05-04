/*! \file monitor.h
  \author Travis Goodspeed
  \brief Debug monitor commands.
*/

#ifndef MONITOR_H
#define MONITOR_H

#include "app.h"

// Monitor application number
#define MONITOR 0x00

// Monitor Commands
#define MONITOR_CHANGE_BAUD 0x80
#define MONITOR_ECHO 0x81
#define MONITOR_LIST_APPS 0x82
#define MONITOR_RAM_PATTERN 0x90
#define MONITOR_RAM_DEPTH 0x91

#define MONITOR_DIR 0xA0
#define MONITOR_OUT 0xA1
#define MONITOR_IN  0xA2

#define MONITOR_SILENT 0xB0
#define MONITOR_CONNECTED 0xB1

#define MONITOR_READBUF 0xC0
#define MONITOR_WRITEBUF 0xC1
#define MONITOR_SIZEBUF 0xC2

#define MONITOR_LEDTEST 0xD0

extern app_t const monitor_app;

#endif // MONITOR_H

