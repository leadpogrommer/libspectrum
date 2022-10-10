#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "UsbRawSpectrometer.h"

PYBIND11_MODULE(pyspectrum, m){
    pybind11::class_<UsbRawSpectrometer>(m, "Device")
            .def(pybind11::init<int, int>())
            .def("readFrame", &UsbRawSpectrometer::readFrame);
}