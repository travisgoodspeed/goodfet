	;; Org is set at 0 so that there is no padding before the sled.
	;; This code should be run from RAM; the address doesn't really matter.
	BASE == 0x0
	.org BASE
	code_size_guess == 0xB2
	LED_PORT = 0x0200
	FLASH_LED = 0x02
	FAIL_LED = 0x04

	;; MSP430f5510 definitions
	FCTL1 == 0x0140
	FCTL3 == 0x0144
	BUSY == 0x0001
	FWPW == 0xA500
	ERASE == 0x0004
	WRT == 0x0040
	BLKWRT == 0x0080
	WAIT == 0x0008
	LOCK == 0x0010

	;; Format of payload: (all values MSP-endian)
	;; {
	;;   number of blocks: 1 byte
	;;   checksum: 1 byte (byte such that two's complement sum of payload bytes == 0xff)
	;;   repeat: (total of (payload length - 3) bytes)
	;;     (start_address >> 8): 2 bytes
	;;     block data: 512 bytes
	;; }
	;; The shortest possible payload would thus be <<0x00 0xFF>>
	;; A payload that writes 0's to 0xFE00-0xFFFF would be:
	;;    <<0x01 0x00 0xFE 0x00 0x00*512>>

	;; Assumptions/caveats:
	;; 1) Assume RAM is in low memory. It will fail miserably otherwise
	;; 2) All this code is very carefully written to be position-independent

	;; Register usage:
	;;
	;; r4: start of payload
	;; r5: address of start
start:
	;; the next two instructions must be the first two instructions after start
	mov	r0, r5
	add	#(code_size_guess + start - .), r5
	mov	r6, r4

	bis.b	#FLASH_LED+FAIL_LED, &LED_PORT+4
	bic.b	#FLASH_LED+FAIL_LED, &LED_PORT+2
	;; calc checksum
	;; local regs:
	;; r6: running sum
	;; r7: end addr
	;; r8: current addr
	;; r9: scratch
	mov	r4, r8
	mov	r4, r7
	mov.b	@r8, r9
	incd	r7

	rla	r9, 1		; Add r9*514 (r9<<1 + r9 << 9)
	add	r9, r7
	rla	r9, 8
	add	r9, r7

	add	@r8, r7
	mov.b	#0, r6
1:	add.b	@r8+, r6
	cmp	r7, r8
	jlo	1b
	cmp	#0xff, r6

	bis.b	#FAIL_LED, &LED_PORT+2
	reta

	;; Get flashing
	;; local regs:
	;; r6: current src
	;; r7: current dest
	;; r8: block id
	;; r9: block count
	;; r10: dwords remaining
	mov	r4, r6
	clr	r8
	mov.b	@r4, r9
	incd	r6

next_block:
	dec	r9
	jnc	done_programming
	bis	#FLASH_LED, &LED_PORT+2
	;; calc dest addr
	mov	@r6+, r7
	rlam.a	#4, r7		; multiply by 256 to recover real address
	rlam.a	#4, r7
	;; erase block
1:	bit	#BUSY, &FCTL3
	jnz	1b
	mov	#FWPW, &FCTL3
	mov	#FWPW+ERASE, &FCTL1
	clr	@r7
1:	bit	#BUSY, &FCTL3
	jnz	1b

	;; not sure whether I need to bounce LOCK here
	mov	#32, r10
	mov	#FWPW+BLKWRT+WRT, &FCTL1
2:	mov	@r6+, 0(r7)
	mov	@r6+, 2(r7)
3:	bit	#WAIT, &FCTL3
	jz	3b
	add	#4, r7 		; This was originally 2 incd insns
	dec	r10
	jnz	2b
	mov	#FWPW, &FCTL1
4:	bit	#BUSY, &FCTL3
	jnz	4b

	mov	#FWPW+LOCK, &FCTL3
	jmp	next_block

done_programming:
	bic.b	#FLASH_LED, &LED_PORT+2
	bic.b	#FAIL_LED, &LED_PORT+2

bsl_ret:
	mov	#2, r12
	mov	#0xDEAD, r13
	mov	#0xBEEF, r14
	bra	#0x1002

payload:
	.data
	.if (payload-start) != code_size_guess

	.print "Payload guess wrong"
	.endif


