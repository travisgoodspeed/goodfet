/*! \file cc2500.h
  \author Jean-Michel Picod
  \brief Constants for CC2500 SPI Driver
*/

#ifndef CC2500_H
#define CC2500_H

#include "app.h"

#define CC2500 0x52

//Chipcon SPI Commands

//Grab a packet, if one is available.
#define CC2500_RX 0x80
//Keep grabbing packets, ignoring further commands.
#define CC2500_REPEAT_RX 0x91
//Send a packet.
#define CC2500_TX 0x81
//Flush RX
#define CC2500_RX_FLUSH 0x82
//Flush TX
#define CC2500_TX_FLUSH 0x83

//Register definitions might go here, at least for buffers.
#define CC2500_TXFIFO  0x3F
#define CC2500_RXFIFO  0xBF
#define CC2500_SFLUSHRX 0x3A
#define CC2500_SFLUSHTX 0x3B

// Strobes
#define CC2500_SRX 0x34
#define CC2500_STX 0x35
#define CC2500_SNOP 0x3D
#define CC2500_SIDLE 0x36

#define CC2500_RXBYTES 0xFB // WARN: Burst bit is ON !

extern app_t const cc2500_app;

#endif // CC2500_H

