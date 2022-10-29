#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "UsbRawSpectrometer.h"

namespace py = pybind11;

PYBIND11_MODULE(PYMODULE_NAME, m){
    py::class_<RawSpectrometer>(m, "RawSpectrometer")
            .def("readFrame", &RawSpectrometer::readFrame)
            .def("getPixelCount", &RawSpectrometer::getPixelCount)
            .def("setTimer", &RawSpectrometer::setTimer);

    py::class_<UsbRawSpectrometer, RawSpectrometer>(m, "UsbRawSpectrometer")
            .def(pybind11::init<int, int>());

    py::class_<RawSpectrum>(m, "RawSpectrum")
            .def_property_readonly("samples", &RawSpectrum::pyGetSamples)
            .def_property_readonly("clipped", &RawSpectrum::pyGetClipped);
}