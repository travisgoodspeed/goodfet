
READ = 0
WRITE = 1

platforms = {
    "at91sam7": {0x000000: (0x100000, "Flash before remap, SRAM after remap"),
                 0x100000: (0x100000, "Internal Flash"),
                 0x200000: (0x100000, "Internal SRAM"),
                 },
    "at91r40008":{0x000000: (0x100000, "Flash before remap, SRAM after remap"),
                 0x100000: (0x100000, "Internal Flash"),
                 0x200000: (0x100000, "Internal SRAM"),
                 0x300000: (0x100000, "Internal SRAM - pre-remap"),
                 0x400000: (0xfc000000-0x400000, "External Bus Interface Addressing"),
                 },
    }

# gratuitously leveraged from atmel's Flash_uploader demo app
EB40_EBI_desc = (
        ( WRITE, 0xFFE00000, 0x01002529 ),  #* Write EBI_CSR0
        ( WRITE, 0xFFE00004, 0x02002121 ),  #* Write EBI_CSR1
        ( WRITE, 0xFFE00020, 0x00000001 ),  #* Remap Command
        ( WRITE, 0xFFE00024, 0x00000006 )   #* Memory Control Register 
)

EB40A_EBI_desc = (
        ( WRITE, 0xFFE00000, 0x01002539 ),  #* Write EBI_CSR0  0x01002539
        ( WRITE, 0xFFE00020, 0x00000001 ),  #* Remap Command
        ( WRITE, 0xFFE00024, 0x00000006 )   #* Memory Control Register 
)

EB42_EBI_desc = (
        ( WRITE, 0xFFE00000, 0x01002529 ),  #* Write EBI_CSR0
        ( WRITE, 0xFFE00004, 0x02002121 ),  #* Write EBI_CSR1
        ( WRITE, 0xFFE00020, 0x00000001 ),  #* Remap Command
        ( WRITE, 0xFFE00024, 0x00000006 )   #* Memory Control Register 
)

EB55_EBI_desc = (
        ( WRITE, 0xFFE00000, 0x01002529 ),  #* Write EBI_CSR0
        ( WRITE, 0xFFE00004, 0x02002121 ),  #* Write EBI_CSR1
        ( WRITE, 0xFFE00020, 0x00000001 ),  #* Remap Command
        ( WRITE, 0xFFE00024, 0x00000006 )   #* Memory Control Register 
)

EB63_EBI_desc = (
        ( WRITE, 0xFFE00000, 0x01002529 ),  #* Write EBI_CSR0
        ( WRITE, 0xFFE00004, 0x02002121 ),  #* Write EBI_CSR1
        ( WRITE, 0xFFE00020, 0x00000001 ),  #* Remap Command
        ( WRITE, 0xFFE00024, 0x00000006 )   #* Memory Control Register 
)

EB42_PLL_desc = (
        #* Disable external watchdog assertion
        ( WRITE, 0xFFFF8008, 0x00000000 ),  #* ST_WMR

        #* Set up the Clock frequency to run at 32,768 MHz with PLLB
        ( WRITE, 0xFFFF4020, 0xC503E708 ),  #* PMC_CGMR

        #* Reading the PMC Status register to detect when the PLLB is stabilized
        ( POLL, 0xFFFF4030, 0x00000001 ),   #* PMC_SR

        #* Commuting from Slow Clock to PLLB
        ( WRITE, 0xFFFF4020, 0xC503E798 )   #* PMC_CGMR
)

EB55_PLL_desc = (
        #* Enable the main oscillator (16Mhz) / MOSCEN = 1, OSCOUNT = 47  (1.4ms/30µs)
        ( WRITE, 0xFFFF4020, 0x002F0002 ),  #* APMC_CGMR

        #* Wait for Main oscillator stabilization. Wait for APMC_MOSCS Bit in APMC_SR equals 1
        ( POLL, 0xFFFF4030, 0x00000001 ),   #* APMC_SR

        #* Commuting from Slow Clock to Main Oscillator (32K to 16Mhz)
        ( WRITE, 0xFFFF4020, 0x002F4002 ),  #* APMC_CGMR

        #* Setup the PLL / MUL = 1, PLLCOUNT = 3, CSS = 1
        ( WRITE, 0xFFFF4020, 0x032F4102 ),  #* APMC_CGMR

        #* Wait for the PLL is stabilized. Wait for APMC_PLL_LOCK Bit in APMC_SR equals 1
        ( POLL, 0xFFFF4030, 0x00000002 ),   #* APMC_SR

        #* Commuting from 16Mhz to PLL @ 32MHz / CSS = 2, MUL = 1
        ( WRITE, 0xFFFF4020, 0x032F8102 )   #* APMC_CGMR
)


{
    {
        EB40,
        { NULL, 0 },
        { EB40_EBI_desc, sizeof(EB40_EBI_desc)/sizeof(Instr) },
        FLASH_LV,
        {(u_int *)FLASH_LV_PRG, 0x7D0, 0x20 },  //* Flash algo
        {(u_int *)0x0101C000, 0x7D0, 0x20 },    //* Flash identify
        {(u_int *)0x01020000, 0x800, 0x0 },     //* boot 2KB
        {(u_int *)0x01030000, 0xCD00, 0x2000 }, //* angel 51KB
        {(u_int *)0x01028000, 0x1800, 0x00010000 }, //* appli 6KB
        { NULL, 0, 0 }  //* Mirror
    },  
    {
        EB40A,
        { NULL, 0 },
        { EB40A_EBI_desc, sizeof(EB40A_EBI_desc)/sizeof(Instr) },
        FLASH_BV,
        {(u_int *)FLASH_BV_PRG, 0x7D0, 0x20 },  //* Flash algo
        {(u_int *)0x0101E000, 0x400, 0x20 },    //* Flash identify
        {(u_int *)0x01040000, 0x2800, 0x01000000 }, //* boot 10KB
        {(u_int *)0x01050000, 0xCD00, 0x01006000 }, //* angel 51KB
        {(u_int *)0x01048000, 0x1800, 0x01100000 }, //* appli 4KB
        {(u_int *)0x01000000, 0x200000 , 0x01000000 }   //* Mirror
    },
    {
        EB42,
        { EB42_PLL_desc, sizeof(EB42_PLL_desc)/sizeof(Instr) },
        { EB42_EBI_desc, sizeof(EB42_EBI_desc)/sizeof(Instr) },
        FLASH_BV,
        {(u_int *)FLASH_BV_PRG, 0x7D0, 0x20 },  //* Flash algo
        {(u_int *)0x0101E000, 0x400, 0x20 },    //* Flash identify
        {(u_int *)0x01060000, 0x3400, 0x01000000 }, //* boot 13KB
        {(u_int *)0x01070000, 0xCD00, 0x01006000 }, //* angel 51KB
        {(u_int *)0x01068000, 0x1800, 0x01100000 }, //* appli 4KB 0x1170000 0x1100000
        { NULL, 0, 0 }  //* Mirror
    },  
    {
        EB55,
        { EB55_PLL_desc, sizeof(EB55_PLL_desc)/sizeof(Instr) },
        { EB55_EBI_desc, sizeof(EB55_EBI_desc)/sizeof(Instr) },
        FLASH_BV,
        {(u_int *)FLASH_BV_PRG, 0x7D0, 0x20 },  //* Flash algo
        {(u_int *)0x0101E000, 0x400, 0x20 },    //* Flash identify
        {(u_int *)0x01080000, 0x4C00, 0x01000000 }, //* boot 19KB
        {(u_int *)0x01090000, 0xCD00, 0x01006000 }, //* angel 51KB
        {(u_int *)0x01088000, 0x1800, 0x01100000 }, //* appli 4KB
        { NULL, 0, 0 }  //* Mirror
    },
    {
        EB63,
        { NULL, 0 },
        { EB63_EBI_desc, sizeof(EB63_EBI_desc)/sizeof(Instr) },
        FLASH_BV,
        {(u_int *)FLASH_BV_PRG, 0x7D0, 0x20 },  //* Flash algo
        {(u_int *)0x0101E000, 0x400, 0x20 },    //* Flash identify
        {(u_int *)0x010A0000, 0x2800, 0x01000000 }, //* boot 10KB
        {(u_int *)0x010B0000, 0xCD00, 0x01004000 }, //* angel 51KB
        {(u_int *)0x010A8000, 0x1800, 0x01100000 }, //* appli 4KB
        { NULL, 0, 0 }  //* Mirror
    }

};

IV_RESET    =   0
IV_ABORT    =   4
IV_DABORT   =   8
IV_PREFETCH =   12
IV_UNDEF    =   16
IV_FIQ      =   20

