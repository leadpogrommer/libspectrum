#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Device.h"

PYBIND11_MODULE(c_test, m){
    pybind11::class_<Device>(m, "Device")
            .def(pybind11::init())
            .def("init", &Device::init)
            .def("readFrame", &Device::readFrame);
}