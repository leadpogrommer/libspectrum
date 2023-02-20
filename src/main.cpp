#include <vector>
#include <algorithm>
#include <cstdint>
#include <iostream>

#include "UsbRawSpectrometer.h"

int main() {
    UsbRawSpectrometer device(0x0403, 0x6014);

    device.readFrame(1);
    auto frame = device.readFrame(1).samples;
    std::for_each(frame.begin(), frame.end(),
                    [](uint16_t a) { std::cout << a << std::endl; });

    return 0;
}
