/*
 * Copyright 2010 Michael Ossmann
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

#define u8 unsigned char
#define u16 unsigned int
#define u32 unsigned long

/*
 * There is one channel per column of the display.  The radio is tuned to one
 * channel at a time and RSSI is displayed for that channel.
 */
//#define NUM_CHANNELS 132
#define NUM_CHANNELS 10

/*
 * wide mode (default): 44 MHz on screen, 333 kHz per channel
 * narrow mode: 6.6 MHz on screen, 50 kHz per channel
 */
#define WIDE 0
#define NARROW 1
#define ULTRAWIDE 2

/*
 * short mode (default): displays RSSI >> 2
 * tall mode: displays RSSI
 */
#define SHORT 0
#define TALL 1

/* vertical scrolling */
#define SHORT_STEP  16
#define TALL_STEP   4
#define MAX_VSCROLL 208
#define MIN_VSCROLL 0

/* frequencies in MHz */
#define DEFAULT_FREQ     915
#define WIDE_STEP        5
#define NARROW_STEP      1
#define ULTRAWIDE_STEP   20
#define WIDE_MARGIN      13
#define NARROW_MARGIN    3
#define ULTRAWIDE_MARGIN 42

/* frequency bands supported by device */
#define BAND_300 0
#define BAND_400 1
#define BAND_900 2

/* band limits in MHz */
#define MIN_300  281
#define MAX_300  361
#define MIN_400  378
#define MAX_400  481
#define MIN_900  749
#define MAX_900  962

/* band transition points in MHz */
#define EDGE_400 369
#define EDGE_900 615

/* VCO transition points in Hz */
#define MID_300  318000000
#define MID_400  424000000
#define MID_900  848000000

/* channel spacing in Hz */
#define WIDE_SPACING      199952
#define NARROW_SPACING    49988
#define ULTRAWIDE_SPACING 666504

#define MIN(a, b)  (((a) < (b)) ? (a) : (b))
#define MAX(a, b)  (((a) > (b)) ? (a) : (b))


/* Keeping track of all this for each channel allows us to tune faster. */
typedef struct {
	/* frequency setting */
	u8 freq2;
	u8 freq1;
	u8 freq0;
	
	/* frequency calibration */
	u8 fscal3;
	u8 fscal2;
	u8 fscal1;

	/* signal strength */
	u8 ss;
	u8 max;
} channel_info;

void clear();
void plot(u8 col);
void putchar(char c);
u8 getkey();
void draw_ruler();
void draw_freq();
void radio_setup();
void set_filter();
void set_radio_freq(u32 freq);
void calibrate_freq(u32 freq, u8 ch);
u16 set_center_freq(u16 freq);
void tune(u8 ch);
void set_width(u8 w);
void poll_keyboard();
void main(void);
