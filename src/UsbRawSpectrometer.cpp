#include "UsbRawSpectrometer.h"

UsbRawSpectrometer::UsbRawSpectrometer(int vendor, int product) {
    context.open(vendor, product);
    context.set_bitmode(BITMODE_SYNCFF, BITMODE_SYNCFF);
    context.set_usb_read_timeout(300);
    context.set_usb_write_timeout(300);
    sendCommand(COMMAND_WRITE_CR, 0);
    sendCommand(COMMAND_WRITE_TIMER, 0x03e8);
    sendCommand(COMMAND_WRITE_PIXEL_NUMBER, pixel_number);
}


void UsbRawSpectrometer::setTimer(unsigned long millis) {
 // TODO: not implemented
}

unsigned int UsbRawSpectrometer::getPixelCount() {
    return pixel_number;
}

RawSpectrum UsbRawSpectrometer::readFrame(int n_times) {
    RawSpectrum ret{
        getPixelCount(),
        static_cast<unsigned int>(n_times),
        std::vector<int>(n_times*getPixelCount()),
        std::vector<uint8_t>(n_times*getPixelCount()),
        };
//    std::cout << "Cpp: RawSpectrum created" << std::endl;
    std::vector<uint16_t> data(pixel_number);
    for(int i = 0; i < n_times; i++){
        sendCommand(COMMAND_READ_FRAME, 1);
        readData(reinterpret_cast<uint8_t *>(data.data()), pixel_number * 2);
        std::transform(data.begin(), data.end(), ret.clipped.begin() + (getPixelCount()*i), [](uint16_t n){return n == UINT16_MAX;});
        std::copy(data.begin(), data.end(), ret.samples.begin() + (getPixelCount()*i));
    }

    return ret;
}

DeviceReply UsbRawSpectrometer::sendCommand(uint8_t code, uint32_t data) {
    DeviceCommand command  = {{'#', 'C', 'M', 'D'}, code, 4, sequenceNumber, data};
    context.write(reinterpret_cast<unsigned char *>(&command), sizeof(DeviceCommand));
    DeviceReply reply{};
    readExactly(reinterpret_cast<unsigned char *>(&reply), sizeof(DeviceReply));
    return reply;
}

void UsbRawSpectrometer::readData(uint8_t *buffer, size_t amount) {
    size_t dataRead = 0;
    while (dataRead < amount){
        DeviceDataHeader header{};
        readExactly(reinterpret_cast<unsigned char *>(&header), sizeof(header));
        if(header.length > (amount - dataRead)){
            throw std::overflow_error("Trying to read more data than expected");
        }
        readExactly(buffer + dataRead, header.length);
        dataRead += header.length;
    }
}

void UsbRawSpectrometer::readExactly(uint8_t *buff, int amount) {
    int wasRead = 0;
    while (wasRead != amount){
        wasRead += context.read(buff + wasRead, amount - wasRead);

    }
}