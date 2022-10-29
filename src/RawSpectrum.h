#pragma once
#include <vector>
#include "pybind11/pybind11.h"
#include "pybind11/numpy.h"
#include <iostream>

namespace py = pybind11;

struct RawSpectrum {
    unsigned int n_samples;
    unsigned int n_measures;
    std::vector<int> samples;
    std::vector<uint8_t> clipped;

    py::array_t<int> pyGetSamples(){
        return py::array_t<int>(
                {n_measures, n_samples},
                {n_samples * sizeof(int), sizeof(int)},
                samples.data()
                );
    }

    py::array_t<uint8_t> pyGetClipped(){
        return py::array_t<uint8_t>(
                {n_measures, n_samples},
                {n_samples * sizeof(uint8_t), sizeof(uint8_t)},
                clipped.data()
        );
    }


//    ~RawSpectrum(){
//        std::cout << "Cpp: RawSpectrum destroyed" << std::endl;
//    }
};


