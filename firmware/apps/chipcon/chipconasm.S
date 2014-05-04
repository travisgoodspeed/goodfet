.globl ccdebuginit
.type ccdebuginit,@function //for linking

#define _GNU_ASSEMBLER_
#include "gfports.h"

	
//In assembly for cycle-counting, not for efficiency.
//
ccdebuginit:
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	nop			;1 cycle
	
	bis.b	#13,	&0x0031	;5 cycles
	bic.b	#8,	&0x0031	;4 cycles
	bic.b	#1,	&0x0031	;4
	xor.b	#8,	&0x0031	;4
	xor.b	#8,	&0x0031	;4
	xor.b	#8,	&0x0031	;4
;; 	xor.b	#8,	&0x0031	;4
	bis.b	#1,	&0x0031	;4
	ret			
