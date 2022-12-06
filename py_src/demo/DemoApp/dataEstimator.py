import string

import numpy as np

from pyspectrum_mock import Spectrum


class DataEstimator:
    VIN_CONSTANT_B=0.002897771955
    def __init__(self):
        pass
    def calculate(self,spectrum:Spectrum):
        peak_wave=self.peak_wave_calculate(spectrum)
        color_temperature=self.vine_temperature_calculate(peak_wave[1])
        result=np.array([peak_wave,color_temperature])
        return result
    def peak_wave_calculate(self, spectrum: Spectrum)->(string, float):
        return ("Peak wave",spectrum.wavelength[np.argmax(np.mean(spectrum.samples, axis=0))])
    def vine_temperature_calculate(self, peak_wave_length:float)->(string, float):
        return ("Color temperature", self.VIN_CONSTANT_B * 1000000000.0 / peak_wave_length)

