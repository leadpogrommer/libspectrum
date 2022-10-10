#include <iostream>
#include <ftdi.hpp>
#include <cstring>
#include <exception>
#include <vector>

#include "UsbRawSpectrometer.h"

int main() {

    UsbRawSpectrometer device(0x0403, 0x6014);

    device.readFrame();
    auto frame = device.readFrame();
    std::for_each(frame.begin(), frame.end(), [](uint16_t a){
        std::cout << a << std::endl;
    });


    return 0;
}
