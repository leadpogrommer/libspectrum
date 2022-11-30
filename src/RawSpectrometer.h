#pragma once

#include <vector>
#include <cinttypes>
#include "RawSpectrum.h"

class RawSpectrometer {
public:
    virtual void setTimer(unsigned long millis) = 0;
    virtual unsigned int getPixelCount() = 0;
    virtual RawSpectrum readFrame(int n_times) = 0;
};