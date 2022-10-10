#include <vector>
#include <cinttypes>

class RawSpectrometer{
    virtual void setTimer(unsigned long millis) = 0;
    virtual unsigned int getPixelCount() = 0;
    virtual std::vector<uint16_t> readFrame() = 0;
};