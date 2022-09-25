#pragma once

#include <cinttypes>
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

// TODO: endianness check
class DeviceCommunication {
public:
    DeviceCommunication(int vendor, int product);

    DeviceReply sendCommand(uint8_t code, uint32_t data);

    void readData(uint8_t *buffer, size_t amount);


private:
    uint16_t sequenceNumber = 1;
    Ftdi::Context context;

    void readExactly(uint8_t *buff, int amount);
};


class Device{
public:
    const int pixel_number = 0x1006;
    void init();

    std::vector<uint16_t >readFrame();


private:
    DeviceCommunication comm = DeviceCommunication(0x0403, 0x6014);
};