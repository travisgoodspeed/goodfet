//
// Created by Thomas Tannhaeuser on 12/23/15.
//

#include "command.h"

#ifdef __MSPGCC__
#include <msp430.h>
/* #else */
/* #include <signal.h> */
/* #include <msp430.h> */
/* #include <iomacros.h> */
#endif

#include "raw.h"

#include "platform.h"

void raw_handle_fn( uint8_t const app,
                    uint8_t const verb,
                    uint32_t const len);

app_t const raw_app = {
    .app = RAW,
    .handle = raw_handle_fn,
    .name = "RAW",
    .desc = "\tThe RAW app offers raw access to the I/O pins of the GoodFET.\n"
};

/**
 * \brief set the state of all selected pins t high
 * \param [in] what bit mask containing pins the state should be set to high
 * \note the set is done regardless the configured direction (input|output) of the selected pins
 */
static void _raw_set(unsigned char what)
{
    if (what & FLAG_TDO) {
        RAW_SET_TDO;
    }
    if (what & FLAG_TDI) {
        RAW_SET_TDI;
    }
    if (what & FLAG_TMS) {
        RAW_SET_TMS;
    }
    if (what & FLAG_TCK) {
        RAW_SET_TCK;
    }
    if (what & FLAG_RST) {
        RAW_SET_RST;
    }
    if (what & FLAG_TST) {
        RAW_SET_TST;
    }
    if (what & FLAG_RXD) {
        RAW_SET_RXD;
    }
    if (what & FLAG_TXD) {
        RAW_SET_TXD;
    }
}

/**
 * \brief set the state of all selected pins t low
 * \param [in] what bit mask containing pins the state should be set to low
 * \note the set is done regardless the configured direction (input|output) of the selected pins
 */
static void _raw_clear(unsigned char what)
{
    if (what & FLAG_TDO) {
        RAW_CLR_TDO;
    }
    if (what & FLAG_TDI) {
        RAW_CLR_TDI;
    }
    if (what & FLAG_TMS) {
        RAW_CLR_TMS;
    }
    if (what & FLAG_TCK) {
        RAW_CLR_TCK;
    }
    if (what & FLAG_RST) {
        RAW_CLR_RST;
    }
    if (what & FLAG_TST) {
        RAW_CLR_TST;
    }
    if (what & FLAG_RXD) {
        RAW_CLR_RXD;
    }
    if (what & FLAG_TXD) {
        RAW_CLR_TXD;
    }
}

/**
 * \brief read the state of all selected pins
 * \param [in] what bit mask containing pins the state should be read from
 * \note the read is done regardless the configured direction (input|output) of the selected pins
 */
static unsigned char _raw_read(unsigned char what)
{
    unsigned char rc = 0;
    if (what & FLAG_TDO && RAW_READ_TDO) {
        rc |=  FLAG_TDO;
    }
    if (what & FLAG_TDI && RAW_READ_TDI) {
        rc |=  FLAG_TDI;
    }
    if (what & FLAG_TMS && RAW_READ_TMS) {
        rc |=  FLAG_TMS;
    }
    if (what & FLAG_TCK && RAW_READ_TCK) {
        rc |=  FLAG_TCK;
    }
    if (what & FLAG_RST && RAW_READ_RST) {
        rc |=  FLAG_RST;
    }
    if (what & FLAG_TST && RAW_READ_TST) {
        rc |=  FLAG_TST;
    }
    if (what & FLAG_RXD && RAW_READ_RXD) {
        rc |=  FLAG_RXD;
    }
    if (what & FLAG_TXD && RAW_READ_TXD) {
        rc |=  FLAG_TXD;
    }

    return rc;
}

/**
 * \brief set pin direction to input for all selected pins
 * \param [in] what bit mask containing pins that should set to be an input
 */
static void _raw_set_direction_input(unsigned char what)
{
    if (what & FLAG_TDO) {
        RAW_TDO_DIR_INPUT;
    }
    if (what & FLAG_TDI) {
        RAW_TDI_DIR_INPUT;
    }
    if (what & FLAG_TMS) {
        RAW_TMS_DIR_INPUT;
    }
    if (what & FLAG_TCK) {
        RAW_TCK_DIR_INPUT;
    }
    if (what & FLAG_RST) {
        RAW_RST_DIR_INPUT;
    }
    if (what & FLAG_TST) {
        RAW_TST_DIR_INPUT;
    }
    if (what & FLAG_RXD) {
        RAW_RXD_DIR_INPUT;
    }
    if (what & FLAG_TXD) {
        RAW_TXD_DIR_INPUT;
    }
}

/**
 * \brief set pin direction to output for all selected pins
 * \param [in] what bit mask containing pins that should set to be an output
 */
static void _raw_set_direction_output(unsigned char what)
{
    if (what & FLAG_TDO) {
        RAW_TDO_DIR_OUTPUT;
    }
    if (what & FLAG_TDI) {
        RAW_TDI_DIR_OUTPUT;
    }
    if (what & FLAG_TMS) {
        RAW_TMS_DIR_OUTPUT;
    }
    if (what & FLAG_TCK) {
        RAW_TCK_DIR_OUTPUT;
    }
    if (what & FLAG_RST) {
        RAW_RST_DIR_OUTPUT;
    }
    if (what & FLAG_TST) {
        RAW_TST_DIR_OUTPUT;
    }
    if (what & FLAG_RXD) {
        RAW_RXD_DIR_OUTPUT;
    }
    if (what & FLAG_TXD) {
        RAW_TXD_DIR_OUTPUT;
    }
}

/**
 * \brief set all IO pins to input, disable pull-up/down resistors
 */
static void _raw_setup()
{
    _raw_set_direction_input(TDO_PIN | TDO_PIN | TMS_PIN | TCK_PIN | RST_PIN | TST_PIN | RXD_PIN | TXD_PIN);
    RAW_SET_TDO_IO_FNCT;
    RAW_SET_TDI_IO_FNCT;
    RAW_SET_TMS_IO_FNCT;
    RAW_SET_TST_IO_FNCT;
    RAW_SET_TCK_IO_FNCT;
    RAW_SET_RST_IO_FNCT;
    RAW_SET_RXD_IO_FNCT;
    RAW_SET_TXD_IO_FNCT;
    RAW_TDO_DISABLE_PULL_X_R;
    RAW_TDI_DISABLE_PULL_X_R;
    RAW_TMS_DISABLE_PULL_X_R;
    RAW_TCK_DISABLE_PULL_X_R;
    RAW_RST_DISABLE_PULL_X_R;
    RAW_TST_DISABLE_PULL_X_R;
    RAW_RXD_DISABLE_PULL_X_R;
    RAW_TXD_DISABLE_PULL_X_R;
}

/**
 * \brief execute the verbs of the application raw
 * \param [in] app application identifier
 * \param [in] verb action to be executed
 * \param [in] len of the data placed in cmddata (max. len is CMDDATALEN)
 */
void raw_handle_fn( uint8_t const app,
                    uint8_t const verb,
                    uint32_t const len)
{
    // expect 1 byte of data (containing the pin mask) for all verbs != setup
    if (verb != RAW_CMD_SETUP && len != 1)
    {
        txdata(app, NOK, 0);
        return;
    }

    led_on();

    switch(verb)
    {
        case RAW_CMD_SETUP:
            _raw_setup();
            txdata(app,verb,0);
            led_off();
            return;
        case RAW_CMD_SET_DIR_INPUT:
            _raw_set_direction_input(cmddata[0]);
            txdata(app, OK, 1);
            led_off();
            return;
        case RAW_CMD_SET_DIR_OUTPUT:
            _raw_set_direction_output(cmddata[0]);
            txdata(app, OK, 1);
            led_off();
            return;
        case RAW_CMD_CLEAR:
            _raw_clear(cmddata[0]);
            txdata(app, OK, 1);
            led_off();
            return;
        case RAW_CMD_SET:
            _raw_set(cmddata[0]);
            txdata(app, OK, 1);
            led_off();
            return;
        case RAW_CMD_READ:
            cmddata[1] = _raw_read(cmddata[0]);
            txdata(app, OK, 2);
            led_off();
            return;
    }

    txdata(app, NOK, 0);
}

