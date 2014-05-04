#!/usr/bin/env python

from GoodFETSPI import GoodFETSPI

# registers
MAIN      = 0x00 # Main control register
FSCTRL    = 0x01 # Frequency synthesiser main control and status
FSDIV     = 0x02 # Frequency synthesiser frequency division control
MDMCTRL   = 0x03 # Modem main control and status
AGCCTRL   = 0x04 # AGC main control and status
FREND     = 0x05 # Analog front-end control
RSSI      = 0x06 # RSSI information
FREQEST   = 0x07 # Received signal frequency offset estimation
IOCFG     = 0x08 # I/O configuration register
FSMTC     = 0x0B # Finite state machine time constants
MANAND    = 0x0D # Manual signal AND-override register
FSMSTATE  = 0x0E # Finite state machine information and breakpoint
ADCTST    = 0x0F # ADC test register
RXBPFTST  = 0x10 # Receiver bandpass filters test register
PAMTST    = 0x11 # PA and transmit mixers test register
LMTST     = 0x12 # LNA and receive mixers test register
MANOR     = 0x13 # Manual signal OR-override register
MDMTST0   = 0x14 # Modem test register 0
MDMTST1   = 0x15 # Modem test register 1
DACTST    = 0x16 # DAC test register
AGCTST0   = 0x17 # AGC test register: various control and status
AGCTST1   = 0x18 # AGC test register: AGC timeout
AGCTST2   = 0x19 # AGC test register: AGC various parameters
FSTST0    = 0x1A # Test register: VCO array results and override
FSTST1    = 0x1B # Test register: VC DAC manual control VCO current
                        # constant
FSTST2    = 0x1C # Test register:VCO current result and override
FSTST3    = 0x1D # Test register: Charge pump current etc
MANFIDL   = 0x1E # Manufacturer ID, lower 16 bit
MANFIDH   = 0x1F # Manufacturer ID, upper 16 bit
GRMDM     = 0x20 # Generic radio modem control
GRDEC     = 0x21 # Generic radio decimation control and status
PKTSTATUS = 0x22 # Packet mode status
INT       = 0x23 # Interrupt register
SYNCL     = 0x2C # Synchronisation word, lower 16 bit
SYNCH     = 0x2D # Synchronisation word, upper 16 bit
SXOSCON   = 0x60 # Command strobe register: Turn on XOSC
SFSON     = 0x61 # Command strobe register: Start and calibrate FS and
                        # go from RX/TX to a wait mode where the FS is running.
SRX       = 0x62 # Command strobe register: Start RX
STX       = 0x63 # Command strobe register: Start TX (turn on PA)
SRFOFF    = 0x64 # Command strobe register: Turn off RX/TX and FS
SXOSCOFF  = 0x65 # Command strobe register: Turn off XOSC
FIFOREG   = 0x70 # Write and read data to and from the 32 byte FIFO

# register bits

# status byte
XOSC16M_STABLE       = 6
CS_ABOVE_THRESHOLD_N = 5
SYNC_RECEIVED        = 4
STATUS_CRC_OK        = 3
FS_LOCK              = 2
FH_EVENT             = 0
 
# MAIN (0x00) - Main Control Register
RESET            = 15
FS_FORCE_EN      = 9
RXN_TX           = 8
XOSC32K_BYPASS   = 3
XOSC32K_EN       = 2
XOSC16M_BYPASS   = 1
XOSC16M_FORCE_EN = 0

# FSCTRL (0x01) - Frequency Synthesiser Control and Status
LOCK_THRESHOLD  = 4
CAL_DONE        = 3
CAL_RUNNING     = 2
LOCK_LENGTH     = 1
PLL_LOCK_STATUS = 0

# FSDIV (0x02) - Frequency Synthesiser Frequency Division Control
FREQ_R = 10
FREQ   = 0

# MDMCTRL (0x03) - Modem Control and Status
MOD_OFFSET = 7
MOD_DEV    = 0

# AGCCTRL (0x04) - AGC Control and Status
VGA_GAIN      = 8
AGC_LOCKED    = 3
AGC_LOCK      = 2
AGC_SYNC_LOCK = 1
VGA_GAIN_OE   = 0

# FREND (0x05) - Frontend Control Register
PA_DIFF  = 3
PA_LEVEL = 0

# RSSI (0x06) - RSSI Status and Control Register
RSSI_VAL       = 8
RSSI_CS_THRES  = 2
RSSI_FILT      = 0

# FREQEST (0x07) - Received frequency offset estimation
RX_FREQ_OFFSET = 8

# IOCFG (0x08) - I/O configuration register
GIO6_CFG    = 9
GIO1_CFG    = 3
HSSD_SRC    = 0

# FSMTC (0x0B) - Finite state machine time constants
TC_RXON2AGCEN   = 13
TC_PAON2SWITCH  = 10
TC_PAON2TX      = 6
TC_TXEND2SWITCH = 3
TC_TXEND2PAOFF  = 0

# MANAND (0x0D) - Manual signal AND override register 
VGA_RESET_N     = 15
VCO_LOCK_STATUS = 14
BALUN_CTRL      = 13
RXTX            = 12
PRE_PD          = 11
PA_N_PD         = 10
PA_P_PD         = 9
DAC_LPF_PD      = 8
BIAS_PD         = 7
XOSC16M_PD      = 6
CHP_PD          = 5
FS_PD           = 4
ADC_PD          = 3
VGA_PD          = 2
RXBPF_PD        = 1
LNAMIX_PD       = 0

# FSMSTATE (0x0E) - Finite state machine information and breakpoint
FSM_STATE_BKPT = 8
FSM_CUR_STATE  = 0

# ADCTST (0x0F) - ADC Test Register
ADC_I        = 8
ADC_Q        = 0

# RXBPFTST (0x10) - Receiver Bandpass Filters Test Register
RXBPF_CAP_OE  = 14
RXBPF_CAP_O   = 7
RXBPF_CAP_RES = 0

# PAMTST (0x11) - PA and Transmit Mixers Test Register
VC_IN_TEST_EN   = 12
ATESTMOD_PD     = 11
ATESTMOD_MODE   = 8
TXMIX_CAP_ARRAY = 5
TXMIX_CURRENT   = 3
PA_CURRENT      = 0

# LMTST (0x12) - LNA and receive mixers test register
RXMIX_HGM     = 13
RXMIX_TAIL    = 11
RXMIX_VCM     = 9
RXMIX_CURRENT = 7
LNA_CAP_ARRAY = 5
LNA_LOWGAIN   = 4
LNA_GAIN      = 2
LNA_CURRENT   = 0

# MDMTST0 (0x14) - Modem Test Register 0
TX_PRNG              = 13
TX_1MHZ_OFFSET_N     = 12
INVERT_DATA          = 11
AFC_ADJUST_ON_PACKET = 10
AFC_SETTLING         = 8
AFC_DELTA            = 0

# MDMTST1 (0x15) - Modem Test Register 1
BSYNC_THRESHOLD = 0

# DACTST (0x16) - DAC Test Register
DAC_SRC = 12
DAC_I_O = 6
DAC_Q_O = 0

# AGCTST0 (0x17) - AGC Test Register 0
AGC_SETTLE_BLANK_DN = 13
AGC_WIN_SIZE        = 11
AGC_SETTLE_PEAK     = 7
AGC_SETTLE_ADC      = 3
AGC_ATTEMPTS        = 0

# AGCTST1 (0x18) - AGC Test Register 1
AGC_VAR_GAIN_SAT    = 14
AGC_SETTLE_BLANK_UP = 11
PEAKDET_CUR_BOOST   = 10
AGC_MULT_SLOW       = 6
AGC_SETTLE_FIXED    = 2
AGC_SETTLE_VAR      = 0

# AGCTST2 (0x19) - AGC Test Register 1
AGC_BACKEND_BLANKING = 12
AGC_ADJUST_M3DB      = 9
AGC_ADJUST_M1DB      = 6
AGC_ADJUST_P3DB      = 3
AGC_ADJUST_P1DB      = 0

# FSTST0 (0x1A) - Frequency Synthesiser Test Register 0
RXMIXBUF_CUR          = 14
TXMIXBUF_CUR          = 12
VCO_ARRAY_SETTLE_LONG = 11
VCO_ARRAY_OE          = 10
VCO_ARRAY_O           = 5
VCO_ARRAY_RES         = 0

# FSTST1 (0x1B) - Frequency Synthesiser Test Register 1
RXBPF_LOCUR     = 15
RXBPF_MIDCUR    = 14
VCO_CURRENT_REF = 10
VCO_CURRENT_K   = 4
VC_DAC_EN       = 3
VC_DAC_VAL      = 0

# FSTST2 (0x1C) - Frequency Synthesiser Test Register 2
VCO_CURCAL_SPEED = 13
VCO_CURRENT_OE   = 12
VCO_CURRENT_O    = 6
VCO_CURRENT_RES  = 0

# FSTST3 (0x1D) - Frequency Synthesiser Test Register 3
CHP_TEST_UP       = 13
CHP_TEST_DN       = 12
CHP_DISABLE       = 11
PD_DELAY          = 10
CHP_STEP_PERIOD   = 8
STOP_CHP_CURRENT  = 4
START_CHP_CURRENT = 0

# MANFIDL (0x1E) - Manufacturer ID, Lower 16 Bit
PARTNUML = 12
MANFID   = 0

# MANFIDH (0x1F) - Manufacturer ID, Upper 16 Bit
VERSION  = 12
PARTNUMH = 0

# GRMDM (0x20) - Generic Radio Modem Control and Status
SYNC_ERRBITS_ALLOWED = 13
PIN_MODE             = 11
PACKET_MODE          = 10
PRE_BYTES            = 7
SYNC_WORD_SIZE       = 5
CRC_ON               = 4
DATA_FORMAT          = 2
MODULATION_FORMAT    = 1
TX_GAUSSIAN_FILTER   = 0

# GRDEC (0x21) - Generic Radio Decimation Control and Status
IND_SATURATION = 12
DEC_SHIFT      = 10
CHANNEL_DEC    = 8
DEC_VAL        = 0

# PKTSTATUS (0x22) - Packet Mode Status
SYNC_WORD_RECEIVED = 10
CRC_OK             = 9
ERROR_8_10         = 8
ERRCNT_8_10        = 0

# INT (0x23) - Interrupt Register
FH_POLARITY    = 7
PKT_POLARITY   = 6
FIFO_POLARITY  = 5
FIFO_THRESHOLD = 0

# SYNCL (0x2C) - Sync Word, Lower 16 Bit
SYNCWORDL = 0

# SYNCH (0x2D) - Sync Word, Upper 16 Bit
SYNCWORDH = 0

# GIO signals
PA_EN             = 3 # Active high PA enable signal
PA_EN_N           = 4 # Active low PA enable signal
SYNC_RECEIVED     = 5 # Set if a valid sync word has been received since last
                      # time RX was turned on
PKT               = 6 # Packet status signal See Figure 10, page 28.
CARRIER_SENSE_N   = 10 # Carrier sense output (RSSI above threshold)
CRC_OK            = 11 # CRC check OK after last byte read from FIFO
AGC_EN            = 12 # AGC enable signal
FS_PD             = 13 # Frequency synthesiser power down
RX_PD             = 14 # RX power down
TX_PD             = 15 # TX power down
PKT_ACTIVE        = 22 # Packet reception active
MDM_TX_DIN        = 23 # The TX data sent to modem
MDM_TX_DCLK       = 24 # The TX clock used by modem
MDM_RX_DOUT       = 25 # The RX data received by modem
MDM_RX_DCLK       = 26 # The RX clock recovered by modem
MDM_RX_BIT_RAW    = 27 # The un-synchronized RX data received by modem
MDM_BACKEND_EN    = 29 # The Backend enable signal used by modem in RX
MDM_DEC_OVRFLW    = 30 # Modem decimation overflow
AGC_CHANGE        = 31 # Signal that toggles whenever AGC changes gain.
VGA_RESET_N       = 32 # The VGA peak detectors' reset signal
CAL_RUNNING       = 33 # VCO calibration in progress
SETTLING_RUNNING  = 34 # Stepping CHP current after calibration
RXBPF_CAL_RUNNING = 35 # RX band-pass filter calibration running
VCO_CAL_START     = 36 # VCO calibration start signal
RXBPF_CAL_START   = 37 # RX band-pass filter start signal
FIFO_EMPTY        = 38 # FIFO empty signal
FIFO_FULL         = 39 # FIFO full signal
CLKEN_FS_DIG      = 40 # Clock enable Frequency Synthesiser
CLKEN_RXBPF_CAL   = 41 # Clock enable RX band-pass filter calibration
CLKEN_GR          = 42 # Clock enable generic radio
#FIXME name collision
#XOSC16M_STABLE    = 43 # Indicates that the Main crystal oscillator is stable
XOSC_16M_EN       = 44 # 16 MHz XOSC enable signal
XOSC_16M          = 45 # 16 MHz XOSC output from analog part
CLK_16M           = 46 # 16 MHz clock from main clock tree
CLK_16M_MOD       = 47 # 16 MHz modulator clock tree
CLK_8M16M_FSDIG   = 48 # 8/16 MHz clock tree for fs_dig module
CLK_8M            = 49 # 8 MHz clock tree derived from XOSC_16M
CLK_8M_DEMOD_AGC  = 50 # 8 MHz clock tree for demodulator/AGC
FREF              = 53 # Reference clock (4 MHz)
FPLL              = 54 # Output clock of A/M-counter (4 MHz)
PD_F_COMP         = 55 # Phase detector comparator output
WINDOW            = 56 # Window signal to PD (Phase Detector)
LOCK_INSTANT      = 57 # Window signal latched in PD (Phase Detector) by the
                       # FREF clock
RESET_N_SYSTEM    = 58 # Chip wide reset (except registers)
FIFO_FLUSH        = 59 # FIFO flush signal
LOCK_STATUS       = 60 # The top-level FS in lock status signal
ZERO              = 61 # Output logic zero
ONE               = 62 # Output logic one
HIGH_Z            = 63 # Pin set as high-impedance output

# Initialize FET and set baud rate
client = GoodFETSPI()
client.serInit()
client.SPIsetup()

def print_status(status):
	print "0x%02x:" % status,
	if status:
		if status & (1<<XOSC16M_STABLE):
			print "XOSC16M_STABLE",
		if status & (1<<CS_ABOVE_THRESHOLD_N):
			print "CS_ABOVE_THRESHOLD_N",
		if status & (1<<SYNC_RECEIVED):
			print "SYNC_RECEIVED",
		if status & (1<<STATUS_CRC_OK):
			print "STATUS_CRC_OK",
		if status & (1<<FS_LOCK):
			print "FS_LOCK",
		if status & (1<<FH_EVENT):
			print "FH_EVENT",
		print
	else:
		print "power down"

def status():
	response = client.SPItrans([0x00])
	print_status(ord(response))

def reset():
	client.SPItrans([0x00, 0x00, 0x00])
	response = client.SPItrans([0x00, 0x80, 0x00])
	print_status(ord(response[0]))

def strobe(reg):
	response = client.SPItrans([reg])
	print_status(ord(response[0]))

def set(reg, val):
	response = client.SPItrans([reg, val >> 8, val & 0xff])
	print_status(ord(response[0]))

def get(reg):
	response = client.SPItrans([reg | 0x80, 0x00, 0x00])
	print_status(ord(response[0]))
	print "0x%04x" % ((ord(response[1]) << 8) + ord(response[2]))
	return (ord(response[1]) << 8) + ord(response[2])

def txtest():
	# tx test, prng data source
	reset()
	set(MANAND,  0x7fff)
	set(LMTST,   0x2b22)
	set(MDMTST0, 0x334b) # with PRNG
	set(FSDIV,   0x0989) # 2441 MHz
	set(MDMCTRL, 0x0029) # 160 kHz frequency deviation
	strobe(SXOSCON)
	strobe(SFSON)
	strobe(STX)
	status()

def pretest():
	# tx test, infinite preamble
	reset()
	set(MANAND,  0x7fff)
	set(LMTST,   0x2b22)
	set(MDMTST0, 0x134b) # without PRNG
	set(GRMDM,   0x0ff1) # infinite preamble, GFSK
	set(FSDIV,   0x0989) # 2441 MHz
	set(MDMCTRL, 0x0029) # 160 kHz frequency deviation
	strobe(SXOSCON)
	strobe(SFSON)
	strobe(STX)
	status()

def txnobuf():
	reset()
	set(MANAND,  0x7fff)
	set(LMTST,   0x2b22)
	set(MDMTST0, 0x134b) # without PRNG
	set(GRMDM,   0x0101) # un-buffered mode, GFSK
	set(FSDIV,   0x0989) # 2441 MHz
	set(MDMCTRL, 0x0029) # 160 kHz frequency deviation
	strobe(SXOSCON)
	strobe(SFSON)
	strobe(STX)
	status()

def rxnobuf():
	# Bluetooth RX
	reset()
	set(MANAND,  0x7fff)
	set(LMTST,   0x2b22)
	set(MDMTST0, 0x134b) # without PRNG
	set(GRMDM,   0x0101) # un-buffered mode, GFSK
	set(FSDIV,   0x0988) # 2440 MHz + 1 MHz IF = 2441 MHz
	set(MDMCTRL, 0x0029) # 160 kHz frequency deviation
	strobe(SXOSCON)
	strobe(SFSON)
	strobe(SRX)
	status()

def rxhssd():
	reset()
	set(MANAND,  0x7fff)
	set(LMTST,   0x2b22)
	set(MDMTST0, 0x134b) # without PRNG
	set(GRMDM,   0x1101) # hssd mode
	#set(IOCFG,   0x17e2) # output I/Q
	set(IOCFG,   0x17e3) # output I/Q after digital down-mixing and channel filtering
	strobe(SXOSCON)
	strobe(SFSON)
	strobe(SRX)
	status()

def gio1(val):
	val &= 0x3f
	iocfg = get(IOCFG) & 0xfe07
	iocfg |= (val << 3)
	set(IOCFG, iocfg)

def gio6(val):
	val &= 0x3f
	iocfg = get(IOCFG) & 0x81ff
	iocfg |= (val << 9)
	set(IOCFG, iocfg)

def txpkt():
	# untested
	# copied from C sample code
	reset()
	set(FSCTRL,  0x0010)
	set(FSDIV,   0x0980)
	set(MDMCTRL, 0x0040)
	set(FREND,   0x000F)
	set(RSSI,    0x7FF2)
	set(IOCFG,   0x17E0)
	set(FSMTC,   0x7A94)
	set(MANAND,  0x7FFF)
	set(PAMTST,  0x0803)
	set(LMTST,   0x2B22)
	set(MDMTST0, 0x134B)
	set(MDMTST1, 0x004B)
	set(DACTST,  0x0000)
	set(FSTST0,  0xA210)
	set(FSTST1,  0x1002)
	set(GRMDM,   0x0DF0)
	set(GRDEC,   0x0000)

	strobe(SXOSCON)
	# should wait for XOSC16M_STABLE

	strobe(SFSON)
	# should wait for FS_LOCK

	set(FSDIV, 0x0981) # TX freq 1 MHz higher than RX freq

	fsmstate = get(FSMSTATE) & 0x1f
	if fsmstate == 15:
		# send a packet
		set(FIFOREG, 10)
		set(FIFOREG, 0)
		set(FIFOREG, 1)
		set(FIFOREG, 2)
		set(FIFOREG, 3)
		set(FIFOREG, 4)
		set(FIFOREG, 5)
		set(FIFOREG, 6)
		set(FIFOREG, 7)
		set(FIFOREG, 8)
		set(FIFOREG, 9)
		strobe(STX)
	else:
		print "failed"
