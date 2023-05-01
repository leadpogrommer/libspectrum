#include "UsbRawSpectrometer.h"
#include <chrono>

UsbRawSpectrometer::UsbRawSpectrometer(int vendor, int product, std::string serial, int64_t readTimeout)
    : readTimeout(readTimeout) {
    context.open(vendor, product, serial);
    context.setBitmode(0x40, 0x40);
    context.setTimeouts(300, 300);
    sendCommand(COMMAND_WRITE_CR, 0);
    sendCommand(COMMAND_WRITE_TIMER, 0x03e8);
    sendCommand(COMMAND_WRITE_PIXEL_NUMBER, pixel_number);
}

// 10 bits for significand
// 2 bits for exponent
void UsbRawSpectrometer::setTimer(unsigned long millis) {
    millis *= 10;
    int exponent = 0;
    while (millis >= (1 << 10)) {
        exponent++;
        millis /= 10;
    }
    if (exponent >= 4) {
        throw std::overflow_error("Exposure is to big");
    }
    uint32_t command_data = millis | (exponent << 16);

    sendCommand(COMMAND_WRITE_TIMER, command_data);
}

unsigned int UsbRawSpectrometer::getPixelCount() { return pixel_number; }

RawSpectrum UsbRawSpectrometer::readFrame(int n_times) {
    RawSpectrum ret{
        getPixelCount(),
        static_cast<unsigned int>(n_times),
        std::vector<int>(n_times * pixel_number),
        std::vector<uint8_t>(n_times * pixel_number),
    };
    std::vector<uint16_t> data(pixel_number * n_times);

    sendCommand(COMMAND_READ_FRAME, n_times);
    readData(reinterpret_cast<uint8_t*>(data.data()),
             pixel_number * n_times * 2);

    std::transform(data.begin(), data.end(), ret.samples.begin(),
                   [](uint16_t n) { return n ^ (1 << 15); });
    std::transform(ret.samples.begin(), ret.samples.end(), ret.clipped.begin(),
                   [](uint16_t n) { return n == UINT16_MAX; });

    return ret;
}

DeviceReply UsbRawSpectrometer::sendCommand(uint8_t code, uint32_t data) {
    DeviceCommand command = {
        {'#', 'C', 'M', 'D'}, code, 4, sequenceNumber++, data};
    context.write(reinterpret_cast<unsigned char*>(&command),
                  sizeof(DeviceCommand));
    DeviceReply reply{};
    readExactly(reinterpret_cast<unsigned char*>(&reply), sizeof(DeviceReply));
    if (memcmp(reply.magic, "#ANS", 4) != 0) {
        throw std::runtime_error("Received bad #ANS magic from device");
    }
    return reply;
}

void UsbRawSpectrometer::readData(uint8_t* buffer, size_t amount) {
    size_t dataRead = 0;
    while (dataRead < amount) {
        DeviceDataHeader header{};
        readExactly(reinterpret_cast<unsigned char*>(&header), sizeof(header));
        if (memcmp(header.magic, "#DAT", 4) != 0) {
            throw std::runtime_error("Received bad #DAT magic from device");
        }
        if (header.length > (amount - dataRead)) {
            throw std::overflow_error("Trying to read more data than expected");
        }
        readExactly(buffer + dataRead, header.length);
        dataRead += header.length;
    }
}

static int64_t getCurrentTime() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
               std::chrono::system_clock::now().time_since_epoch())
        .count();
}

void UsbRawSpectrometer::readExactly(uint8_t* buff, int amount) {
    int wasRead = 0;
    int64_t lastSuccessfulRead = getCurrentTime();
    while (wasRead != amount) {
        int chunkSize = context.read(buff + wasRead, amount - wasRead);
        wasRead += chunkSize;
        int64_t currentTime = getCurrentTime();
        if (currentTime - lastSuccessfulRead > readTimeout) {
            throw std::runtime_error("Device read timeout");
        }
    }
}

void UsbRawSpectrometer::close() {
    context.close();
    opened = false;
}
bool UsbRawSpectrometer::isOpened() {
    return opened;
}
