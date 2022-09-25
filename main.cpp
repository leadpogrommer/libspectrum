#include <iostream>
#include <ftdi.hpp>
#include <cstring>
#include <exception>
#include <vector>

#include "Device.h"

int main() {

    Device device;
    device.init();

    device.readFrame();
    auto frame = device.readFrame();
    std::for_each(frame.begin(), frame.end(), [](uint16_t a){
        std::cout << a << std::endl;
    });


    return 0;
}
