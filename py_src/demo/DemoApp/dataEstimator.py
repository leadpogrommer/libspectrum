import numpy as np
from pyspectrum import Spectrum
from aproximations import CIE_XYZ_Func, Scotopic_func

VIN_CONSTANT_B = 0.002897771955
Km_CONSTANT = 683
Light_velocity_constant = 299792458


class DataEstimator:
    def __init__(self):
        pass

    result:dict[str,any] = {}
    @staticmethod
    def addToResult(name: str, value: any):
        DataEstimator.result.update({name:value})

    @staticmethod
    def calculate(spectrum: Spectrum):
        reshaped_spectrum = reshape_spectrum(spectrum)
        X, Y, Z = xyz(reshaped_spectrum)
        CCT = cct(X, Y)
        l_power = luminous_power(reshaped_spectrum)
        peak = peak_wave(spectrum)
        return DataEstimator.result


def reshape_spectrum(spectrum: Spectrum):
    """

    :param spectrum: Spectrum
    :return: spectrum distribution wavelengths from 360 to 830, with step 1 nm, interpolation by nearest neighbor
    """
    reshaped_spectrum = {}
    samples = np.mean(spectrum.samples, axis=0)
    target_wavelength_index = 0
    target_wavelength = 360
    for i in range(len(spectrum.wavelength)):
        if target_wavelength > 830:
            break
        if (abs(target_wavelength - spectrum.wavelength[target_wavelength_index]) >=
                abs(target_wavelength - spectrum.wavelength[i])):
            target_wavelength_index = i
        else:
            reshaped_spectrum.update({target_wavelength: samples[target_wavelength_index] / Light_velocity_constant})
            target_wavelength += 1
    return reshaped_spectrum


def xyz(reshaped_spectrum:dict[int,float]) -> (float, float, float):
    """

    :param reshaped_spectrum: reshaped spectrum to (360,830) format with 1 nm step
    :return: XYZ CIE values
    """
    X = 0.0
    Y = 0.0
    Z = 0.0
    for i in range(380, 780):
        X += reshaped_spectrum[i] * CIE_XYZ_Func[i][2]
        Y += reshaped_spectrum[i] * CIE_XYZ_Func[i][1]
        Z += reshaped_spectrum[i] * CIE_XYZ_Func[i][0]

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)
    z = Z / (X + Y + Z)
    DataEstimator.addToResult(name="X", value=x)
    DataEstimator.addToResult(name="Y", value=y)
    DataEstimator.addToResult(name="Z", value=z)
    return x, y, z


def cct(x: float, y: float) -> float:
    """

    :param X: CIE X
    :param Y: CIE Y
    :param Z: CIE Z
    :return: CCT
    """
    P = (x - 0.332) / (y - 0.1858)
    CCT = 5520.33 - 6823.3 * P + 3525 * P * P - 449 * P * P * P
    DataEstimator.addToResult(name="CCT", value=CCT)
    return CCT


def luminous_power(reshaped) -> float:
    lf = 0.0
    for i in range(380, 780):
        lf += Scotopic_func[i] * reshaped[i]
    lf *= Km_CONSTANT
    DataEstimator.addToResult(name="Luminous power", value=lf)
    return lf


def peak_wave(spectrum: Spectrum) -> float:
    peak=spectrum.wavelength[np.argmax(np.mean(spectrum.samples, axis=0))]
    DataEstimator.addToResult(name="Peak", value=peak)
    return peak
