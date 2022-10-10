#pragma once

#include "RawSpectrometer.h"
#include "Spectrum.h"

class Spectrometer{
    // This class will handle profiling, dark calibration & probably more things
    // Now it does nothing

public:
    Spectrometer(RawSpectrometer *spectrometer);
    // should read profiling data from file or from string
    void profile();
    // should read dark frame from device
    void readDarkFrame();
    // should set dark frame from user
    void setDarkFrame();

    void setTImer();
    Spectrum readFrame();

    // maybe i forgot something


private:
    RawSpectrometer *spectrometer;
};
