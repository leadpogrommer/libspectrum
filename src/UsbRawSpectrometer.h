#pragma once

#include "RawSpectrometer.h"
#include <ftdi.hpp>


#define COMMAND_WRITE_CR 0x01
#define COMMAND_WRITE_TIMER 0x02
#define COMMAND_WRITE_PIXEL_NUMBER 0x0c
#define COMMAND_READ_ERRORS 0x92
#define COMMAND_READ_VERSION 0x91
#define COMMAND_READ_FRAME 0x05

struct __attribute__ ((packed)) DeviceCommand {
    char magic[4];
    uint8_t code;
    uint8_t length;
    uint16_t sequenceNumber;
    uint32_t data;
};

struct __attribute__ ((packed)) DeviceReply {
    char magic[4];
    char code;
    uint8_t length;
    uint16_t sequenceNumber;
    uint16_t data;
};

struct __attribute__ ((packed)) DeviceDataHeader {
    char magic[4];
    uint16_t length;
};


class UsbRawSpectrometer: public RawSpectrometer {
public:
    UsbRawSpectrometer(int vendor, int product);

    void setTimer(unsigned long millis) override;

    unsigned int getPixelCount() override;

    RawSpectrum readFrame(int n_times) override;

private:
    const int pixel_number = 0x1006;
    uint16_t sequenceNumber = 1;
    Ftdi::Context context;

    void readExactly(uint8_t *buff, int amount);
    DeviceReply sendCommand(uint8_t code, uint32_t data);
    void readData(uint8_t *buffer, size_t amount);
};



