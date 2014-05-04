#ifndef _msp430_serial_h
#define _msp430_serial_h
/* Name: msp430_serial_h
 * Tabsize: 8
 * Copyright: (c) 2011 by Peter@Lorenzen.us
 * License: [BSD]eerware
 */

#include <stdint.h>

#ifndef FALSE
#  define FALSE 0
#endif
#ifndef TRUE
#  define TRUE 1
#endif
#ifndef NULL
#  define NULL  ((void *) 0)
#endif

#define FIFO_SZ 64		// power of 2
typedef struct fifo {
        uint8_t i;
        uint8_t o;
        volatile uint8_t count, empty;
        uint8_t b[FIFO_SZ];     // buffer
} fifo_t;

extern fifo_t fiforx0;
extern fifo_t fifotx0;
extern fifo_t fiforx1;
extern fifo_t fifotx1;
extern fifo_t *rxfp0;
extern fifo_t *txfp0;
extern fifo_t *rxfp1;
extern fifo_t *txfp1;

void serputc(char c, fifo_t *fp);
void serputs(char *cpt, fifo_t *fp);
void serputb(char c, fifo_t *fp);
void serputw(int w, fifo_t *fp);
int sergetc(fifo_t *fp);
int seravailable(fifo_t *fp);
void serflush(fifo_t *fp);
void ser0_init(int baud, fifo_t *rd, fifo_t *wr);
void ser1_init(int baud, fifo_t *rd, fifo_t *wr);
void serclear(fifo_t *fp);

#ifdef INBAND_DEBUG
#if (DEBUG_LEVEL > 0)
extern char dlevel;
void dputc(char c);
void dputs(char *str);
void dputb(char c);
void dputw(int w);
#else 
#  define dputc(c)
#  define dputs(s)
#  define dputb(b)
#  define dputw(w)
#endif
#  define dflush()
#  define ddflush()
#  define dddflush()
#if (DEBUG_LEVEL > 1)
#  define ddputc(c) if (dlevel>1) dputc(c)
#  define ddputs(s) if (dlevel>1) dputs(s)
#  define ddputb(b) if (dlevel>1) dputb(b)
#  define ddputw(w) if (dlevel>1) dputw(w)
#else 
#  define ddputc(c)
#  define ddputs(s)
#  define ddputb(b)
#  define ddputw(w)
#endif

#if (DEBUG_LEVEL > 2)
#  define dddputc(c) if (dlevel>2) dputc(c)
#  define dddputs(s) if (dlevel>2) dputs(s)
#  define dddputb(b) if (dlevel>2) dputb(b)
#  define dddputw(w) if (dlevel>2) dputw(w)
#else 
#  define dddputc(c)
#  define dddputs(s)
#  define dddputb(b)
#  define dddputw(w)
#endif
#else 

// we use fp1 for debug output
#if (DEBUG_LEVEL > 0)
extern char dlevel;

#  define dputc(c) if (dlevel) serputc(c,txfp1)
#  define dputs(s) if (dlevel) serputs(s,txfp1)
#  define dputb(b) if (dlevel) serputb(b,txfp1)
#  define dputw(w) if (dlevel) serputw(w,txfp1)
#  define dflush() if (dlevel) serflush(txfp1)
#else 
#  define dputc(c)
#  define dputs(s)
#  define dputb(b)
#  define dputw(w)
#  define dflush()
#endif
#if (DEBUG_LEVEL > 1)
#  define ddputc(c) if (dlevel>1) serputc(c,txfp1)
#  define ddputs(s) if (dlevel>1) serputs(s,txfp1)
#  define ddputb(b) if (dlevel>1) serputb(b,txfp1)
#  define ddputw(w) if (dlevel>1) serputw(w,txfp1)
#  define ddflush() if (dlevel>1) serflush(txfp1)
#else 
#  define ddputc(c)
#  define ddputs(s)
#  define ddputb(b)
#  define ddputw(w)
#  define ddflush()
#endif

#if (DEBUG_LEVEL > 2)
#  define dddputc(c) if (dlevel>2) serputc(c,txfp1)
#  define dddputs(s) if (dlevel>2) serputs(s,txfp1)
#  define dddputb(b) if (dlevel>2) serputb(b,txfp1)
#  define dddputw(w) if (dlevel>2) serputw(w,txfp1)
#  define dddflush() if (dlevel>2) serflush(txfp1)
#else 
#  define dddputc(c)
#  define dddputs(s)
#  define dddputb(b)
#  define dddputw(w)
#  define dddflush()
#endif
#endif

#endif
