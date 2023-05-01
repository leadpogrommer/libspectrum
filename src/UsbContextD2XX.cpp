#include <stdexcept>
#include <string>

#include <wtypes.h>
#include <ftd2xx.h>

#include "UsbContext.h"

struct UsbContext::Private {
    FT_HANDLE handle;
};

UsbContext::UsbContext() : p(new Private) {}
UsbContext::~UsbContext() {}

// TODO: open by serial
void UsbContext::open(int vendor, int product, const std::string& serial) {
    DWORD numDevs;
    if (FT_CreateDeviceInfoList(&numDevs) != FT_OK) {
        throw std::runtime_error("Failed to create device info list");
    }

    DWORD id;
    for (DWORD index = 0; index < numDevs; ++index) {
        FT_GetDeviceInfoDetail(index, NULL, NULL, &id, NULL, NULL, NULL, NULL);
        if (((id >> 16) & 0xFFFF) == vendor && (id & 0xFFFF) == product) {
            if (FT_Open(index, &p->handle) != FT_OK) {
                throw std::runtime_error("Failed to open device");
            }
            return;
        }
    }
    throw std::runtime_error("Device not found");
}

void UsbContext::close() {
    if (FT_Close(p->handle) != FT_OK) {
        throw std::runtime_error("Failed to close device");
    }
}

void UsbContext::setBitmode(unsigned char mask, unsigned char enable) {
    if (FT_SetBitMode(p->handle, mask, enable) != FT_OK) {
        throw std::runtime_error("Failed to set bitmode");
    }
}

void UsbContext::setTimeouts(int readTimeoutMillis, int writeTimeoutMillis) {
    if (FT_SetTimeouts(p->handle, readTimeoutMillis, writeTimeoutMillis) != FT_OK) {
        throw std::runtime_error("Failed to set timeouts");
    }
}

int UsbContext::read(unsigned char *buf, int size) {
    DWORD res;
    if (FT_Read(p->handle, buf, size, &res) != FT_OK) {
        throw std::runtime_error("Device read error");
    }
    return res;
}

int UsbContext::write(unsigned char *buf, int size) {
    DWORD res;
    if (FT_Write(p->handle, buf, size, &res) != FT_OK) {
        throw std::runtime_error("Device write error");
    }
    return res;
}
