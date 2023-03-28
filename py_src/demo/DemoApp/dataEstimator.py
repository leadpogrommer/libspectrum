from math import exp

import numpy as np
from pyspectrum import Spectrum
from aproximations import CIE_XYZ_Func, Scotopic_func, color_standards

VIN_CONSTANT_B = 0.002897771955
Km_CONSTANT = 683
Light_velocity_constant = 299792458


class DataEstimator:
    def __init__(self):
        pass

    result: dict[str, any] = {}

    @staticmethod
    def addToResult(name: str, value: any):
        DataEstimator.result.update({name: value})

    @staticmethod
    def calculate(spectrum: Spectrum):
        reshaped_spectrum = reshape_spectrum(spectrum)
        X, Y, Z = xyz(reshaped_spectrum)
        CCT = cct(X, Y)
        l_power = luminous_power(reshaped_spectrum)
        peak = peak_wave(spectrum)
        cri(reshaped_spectrum)
        return DataEstimator.result


def reshape_spectrum(spectrum: Spectrum) -> dict[int, float]:
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
            reshaped_spectrum.update({target_wavelength: samples[target_wavelength_index]})
            target_wavelength += 1
    return reshaped_spectrum


def xyz(reshaped_spectrum: dict[int, float]) -> (float, float, float):
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
    DataEstimator.addToResult(name="x", value=x)
    DataEstimator.addToResult(name="y", value=y)
    DataEstimator.addToResult(name="Y", value=Y)
    return x, y, Y


def cct(x: float, y: float) -> float:
    """

    :param x: CIE x
    :param y: CIE y
    :return: CCT
    """
    P = (x - 0.332) / (y - 0.1858)
    CCT = 5520.33 - 6823.3 * P + 3525 * P * P - 449 * P * P * P
    DataEstimator.addToResult(name="CCT", value=CCT)
    return CCT


def luminous_power(reshaped: dict[int, float]) -> float:
    lf = 0.0
    for i in range(380, 780):
        lf += Scotopic_func[i] * reshaped[i]
    lf *= Km_CONSTANT / Light_velocity_constant
    DataEstimator.addToResult(name="Luminous power", value=lf)
    return lf


def peak_wave(spectrum: Spectrum) -> float:
    """

    :param spectrum: registered spectrum
    :return: the wavelength with max intensity
    """
    peak = spectrum.wavelength[np.argmax(np.mean(spectrum.samples, axis=0))]
    DataEstimator.addToResult(name="Peak", value=peak)
    return peak


def blackbody_sd(reshaped: dict[int, float], cct: float) -> dict[int, float]:
    c1: float = 3.741771e-16
    c2: float = 1.4388e-2
    blackbody = {}
    for i in range(380, 780):
        b=c1*1/(exp(c2/(i*cct))-1)
        blackbody.update({i:b})
    return blackbody


def cie_observer_sd(reshaped: dict[int, float], x: float, y: float) -> dict[int, float]:
    pass


def reference(source_sd: dict[int, float], ref_sd: dict[int, float]):
    result = {}

    def xy_for_colors(sd: dict[int, float], color: dict[int, float]) -> (float, float, float):
        X = 0.0
        Y = 0.0
        Z = 0.0
        for j in range(380, 780,5):
            X += sd[j] * color[j]
            Y += sd[j] * color[j]
            Z += sd[j] * color[j]
        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)
        return x, y, Y

    def d(u: float, v: float) -> float:
        return (1.708 * v - 1.481 * u + 0.404) / v

    def c(u: float, v: float) -> float:
        return (4 - u - 10 * v) / v

    xyY_source = xyz(source_sd)
    uv_source = uv(xyY_source[0], xyY_source[1])

    c_source = c(uv_source[0], uv_source[1])
    d_source = d(uv_source[0], uv_source[1])

    xyY_ref = xyz(ref_sd)
    uv_ref = uv(xyY_ref[0], xyY_ref[1])

    c_ref = c(uv_ref[0], uv_ref[1])
    d_ref = d(uv_ref[0], uv_ref[1])
    for key,i in color_standards.items():
        xyY_source_clr = xy_for_colors(source_sd, i)
        xyY_ref_clr = xy_for_colors(ref_sd, i)

        uv_source_clr = uv(xyY_source_clr[0], xyY_source_clr[1])
        uv_ref_clr = uv(xyY_ref_clr[0], xyY_ref_clr[1])

        c_ref_clr = c(uv_ref_clr[0], uv_ref_clr[1])
        d_ref_clr = d(uv_ref_clr[0], uv_ref_clr[1])

        c_source_clr = c(uv_source_clr[0], uv_source_clr[1])
        d_source_clr = d(uv_source_clr[0], uv_source_clr[1])

        u_source_clr = (10.872 + 0.404 * c_source * c_source_clr / c_ref - 4 * d_source * d_source_clr / d_ref) \
                       / (16.518 + 1.481 * c_source * c_source_clr / c_ref - d_source * d_source_clr / d_ref)
        v_source_clr = 5.52 / (16.518 + 1.481 * c_source * c_source_clr / c_ref - d_source * d_source_clr / d_ref)

        W_s = 25 * pow(xyY_ref_clr[2], 1 / 3) - 17
        U_s = 13 * W_s * (u_source_clr - uv_ref[0])
        V_s = 13 * W_s * (v_source_clr - uv_ref[1])

        W_t = 25 * pow(xyY_ref_clr[2], 1 / 3) - 17
        U_t = 13 * W_t * (uv_ref_clr[0] - uv_ref[0])
        V_t = 13 * W_t * (uv_ref_clr[1] - uv_ref[1])

        dW = (W_t - W_s) * (W_t - W_s)
        dU = (U_t - U_s) * (U_t - U_s)
        dV = (V_t - V_s) * (V_t - V_s)

        dE = pow(dW + dU + dV, 0.5)
        ci = (100 - 4.6 * dE)
        result.update({key: ci})
        DataEstimator.addToResult(f"Color:{key}", ci)
    return result


def cri(reshaped: dict[int, float]) -> float:
    """

    :param x: CIE x
    :param y: CIE y
    :param z: CIE z
    :return: calculated color rendering index
    """

    x, y, Y = xyz(reshaped)
    CCT = cct(x, y)
    if CCT < 5000:
        sd_ref = blackbody_sd(reshaped, CCT)
    else:
        sd_ref = cie_observer_sd(reshaped, x, y)
    colors = reference(reshaped, sd_ref)
    cri = 0.0
    for i in colors.values():
        cri += i
    cri = cri / len(colors.values())
    DataEstimator.addToResult("CRI", cri)
    return cri


def uv(x: float, y: float) -> (float, float):
    u = 4 * x / (12 * y - 2 * x + 3)
    v = 6 * y / (12 * y - 2 * x + 3)
    return u, v
