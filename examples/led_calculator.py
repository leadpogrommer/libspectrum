from math import exp

import numpy as np
from pyspectrum import Spectrum
from aproximations import CIE_XYZ_Func, Scotopic_func, color_standards
import matplotlib.pyplot as plt
from cycler import cycler

VIN_CONSTANT_B = 0.002897771955
Km_CONSTANT = 683
Light_velocity_constant = 299792458
full_angle = 360 * 360 / 3.14


class LedParameters():
    intensity_scale = 80000 * (2 ** 16)
    spectrum = None
    reshaped_spectrum = None
    calibration_XYZ = None
    cc_t = None
    f_l = None
    colors = {}
    XYZ = None
    uv = None
    xyY = None
    flicker_graph = None
    minWL = 400
    maxWL = 830
    """docstring for LedParameters"""

    def __init__(self):
        pass

    def reshape_spectrum(self, spectrum: Spectrum) -> dict[int, float]:

        """

        :param spectrum: Spectrum
        :return: spectrum distribution wavelengths from 360 to 830, with step 1 nm, 
        interpolation by nearest neighbor using mean value on all recorded samples
        """

        reshaped_spectrum = {}
        samples = np.mean(spectrum.intensity, axis=0)
        target_wavelength_index = 0
        target_wavelength = self.minWL
        for i in range(len(spectrum.wavelength)):
            if target_wavelength > self.maxWL:
                break
            if (abs(target_wavelength - spectrum.wavelength[target_wavelength_index]) >=
                    abs(target_wavelength - spectrum.wavelength[i])):
                target_wavelength_index = i
            else:
                tmp = samples[target_wavelength_index]
                # tmp-=self.minI
                # tmp=tmp/(self.maxI-self.minI)
                reshaped_spectrum.update({target_wavelength: tmp})
                target_wavelength += 1

        return reshaped_spectrum

    def non_shaped_spectrum_xyY_calculation(self, spectrum: Spectrum) -> (float, float, float):
        def g(x, u, o1, o2):
            if x < u:
                return exp((-0.5 * (x - u) ** 2) / o1 ** 2)
            else:
                return exp((-0.5 * (x - u) ** 2) / o2 ** 2)

        X = 0.0
        Y = 0.0
        Z = 0.0
        samples = np.mean(spectrum.intensity, axis=0)
        for i in range(len(spectrum.wavelength) - 1):
            X += samples[i] * (
                    1.056 * g(spectrum.wavelength[i], 599.8, 37.9, 31.0) + 0.362 * g(spectrum.wavelength[i], 442.0,
                                                                                     16.0, 26.7) - 0.065 * g(
                spectrum.wavelength[i], 501.1, 20.4, 26.2)) * (spectrum.wavelength[i] - spectrum.wavelength[i + 1])
            Y += samples[i] * (
                    0.821 * g(spectrum.wavelength[i], 568.8, 46.9, 40.5) + 0.286 * g(spectrum.wavelength[i], 530.9,
                                                                                     16.3, 31.1)) * (
                         spectrum.wavelength[i] - spectrum.wavelength[i + 1])
            Z += samples[i] * (
                    1.217 * g(spectrum.wavelength[i], 437.0, 11.8, 36.0) + 0.681 * g(spectrum.wavelength[i], 459.0,
                                                                                     26.0, 13.8)) * (
                         spectrum.wavelength[i] - spectrum.wavelength[i + 1])
        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)
        Y /= self.intensity_scale
        return x, y, Y

    def reshape_spectrum_single(self, spectrum, wavelength) -> dict[int, float]:

        """

        :param spectrum: Spectrum
        :return: spectrum distribution wavelengths from 360 to 830, with step 1 nm, interpolation by nearest neighbor
        """

        reshaped_spectrum = {}
        samples = spectrum
        target_wavelength_index = 0
        target_wavelength = self.minWL
        for i in range(len(spectrum)):
            if target_wavelength > self.maxWL:
                break
            if (abs(target_wavelength - wavelength[target_wavelength_index]) >=
                    abs(target_wavelength - wavelength[i])):
                target_wavelength_index = i
            else:
                tmp = samples[target_wavelength_index]
                reshaped_spectrum.update({target_wavelength: tmp})
                target_wavelength += 1

        return reshaped_spectrum

    def _calculate_xyz(self, reshaped_spectrum) -> (float, float, float):
        X = 0.0
        Y = 0.0
        Z = 0.0
        for i in range(self.minWL, self.maxWL):
            X += reshaped_spectrum[i] * CIE_XYZ_Func[i][0]
            Y += reshaped_spectrum[i] * CIE_XYZ_Func[i][1]
            Z += reshaped_spectrum[i] * CIE_XYZ_Func[i][2]
        x = X / (X + Y + Z)
        y = Y / (X + Y + Z)
        return x, y, Y

    def _calculate_cct(self, x: float, y: float) -> float:

        P = (x - 0.332) / (y - 0.1858)
        CCT = 5520.33 - 6823.3 * P + 3525 * P * P - 449 * P * P * P
        self.cc_t = CCT
        return CCT

    def _calculate_fl(self, spectrum: Spectrum) -> float:

        mx = -100000000
        mn = 100000000
        mxi = 0
        mni = 0
        mean = 0.0
        result_graph = {}
        for i in range(spectrum.n_times):
            tmp = self._calculate_luminous_power(
                self.reshape_spectrum_single(spectrum.intensity[i], spectrum.wavelength))
            mean += tmp
            if tmp > mx:
                mx = tmp
                mxi = i
            if tmp < mn:
                mn = tmp
                mni = i
            result_graph.update({i: tmp})
        mean /= spectrum.n_times
        result_graph.update({mxi: mean})
        result_graph.update({mni: mean})
        mean *= 2
        self.f_l = ((mx - mn) / mean)
        self.flicker_graph = result_graph
        return self.f_l

    def _calculate_luminous_power(self, reshaped) -> float:
        lf = 0.0
        # func=(0.821*g(spectrum.wavelength[i],568.8,46.9,40.5)+0.286*g(spectrum.wavelength[i],530.9,16.3,31.1))*(spectrum.wavelength[i]-spectrum.wavelength[i+1])
        for i in range(self.minWL, self.maxWL):
            lf += Scotopic_func[i] * reshaped[i]
        lf *= Km_CONSTANT / Light_velocity_constant
        return lf

    def blackbody_sd(self, temperature: float) -> dict[int, float]:
        c1: float = 3.741771e-16
        c2: float = 1.4388e-2
        blackbody = {}
        for i in range(self.minWL, self.maxWL):
            j = i * (1e-9)
            b = (j * temperature)
            b = c2 / b
            b = (exp(b) - 1)
            b = c1 / b
            b /= (j ** 5)
            b *= (1e-9)
            blackbody.update({i: b})
        return blackbody

    def reference(self, source_sd: dict[int, float], ref_sd: dict[int, float]):
        result = {}

        def xy_for_colors(sd: dict[int, float], color: dict[int, float]) -> (float, float, float):
            X = 0.0
            Y = 0.0
            Z = 0.0
            k = 0.0
            for j in range(self.minWL, self.maxWL, 5):
                k += color[j] * CIE_XYZ_Func[j][1]
            k = 100 / k
            for j in range(self.minWL, self.maxWL, 5):
                X += sd[j] * color[j] * CIE_XYZ_Func[j][0] * 5
                Y += sd[j] * color[j] * CIE_XYZ_Func[j][1] * 5
                Z += sd[j] * color[j] * CIE_XYZ_Func[j][2] * 5

            X *= k
            Y *= k
            Z *= k
            x = X / (X + Y + Z)
            y = Y / (X + Y + Z)
            Y = Y / self.intensity_scale
            return x, y, Y

        def d(u: float, v: float) -> float:
            return (1.708 * v - 1.481 * u + 0.404) / v

        def c(u: float, v: float) -> float:
            return (4 - u - 10 * v) / v

        xyY_source = self._calculate_xyz(source_sd)
        uv_source = self.calculate_uv(xyY_source[0], xyY_source[1])

        c_source = c(uv_source[0], uv_source[1])
        d_source = d(uv_source[0], uv_source[1])

        xyY_ref = self._calculate_xyz(ref_sd)
        uv_ref = self.calculate_uv(xyY_ref[0], xyY_ref[1])

        c_ref = c(uv_ref[0], uv_ref[1])
        d_ref = d(uv_ref[0], uv_ref[1])
        for key, i in color_standards.items():
            xyY_source_clr = xy_for_colors(source_sd, i)
            xyY_ref_clr = xy_for_colors(ref_sd, i)

            uv_source_clr = self.calculate_uv(xyY_source_clr[0], xyY_source_clr[1])
            uv_ref_clr = self.calculate_uv(xyY_ref_clr[0], xyY_ref_clr[1])

            c_ref_clr = c(uv_ref_clr[0], uv_ref_clr[1])
            d_ref_clr = d(uv_ref_clr[0], uv_ref_clr[1])

            c_source_clr = c(uv_source_clr[0], uv_source_clr[1])
            d_source_clr = d(uv_source_clr[0], uv_source_clr[1])

            u_source_clr = (10.872 + 0.404 * c_source * c_source_clr / c_ref - 4 * d_source * d_source_clr / d_ref) \
                           / (16.518 + 1.481 * c_source * c_source_clr / c_ref - d_source * d_source_clr / d_ref)
            v_source_clr = 5.52 / (16.518 + 1.481 * c_source * c_source_clr / c_ref - d_source * d_source_clr / d_ref)

            W_s = 25 * pow(xyY_source_clr[2], 1 / 3) - 17
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
        self.colors = result
        return result

    def _calculate_cri(self) -> float:

        reshaped = self.reshaped_spectrum

        x, y, Y = self._calculate_xyz(reshaped)
        CCT = self._calculate_cct(x, y)
        sd_ref = self.blackbody_sd(CCT)

        colors = self.reference(reshaped, sd_ref)
        res = 0.0
        len = 0
        for i in colors.values():
            res += i
            len += 1
        res /= len
        self.colors.update({'cri': res})
        return res

    def calculate_uv(self, x: float, y: float) -> (float, float):
        u = 4 * x / (12 * y - 2 * x + 3)
        v = 6 * y / (12 * y - 2 * x + 3)
        return u, v

    def run(self, spectrum: Spectrum):
        self.spectrum = spectrum
        self.reshaped_spectrum = self.reshape_spectrum(spectrum)
        x, y, Y = self.non_shaped_spectrum_xyY_calculation(spectrum)
        self._calculate_cct(x, y)
        self._calculate_fl(spectrum)
        self._calculate_cri()
        return self.cc_t, self.f_l, self.colors

    def get_cri(self):
        return self.result['cri']

    def get_colors(self):
        return self.result

    def get_flicker_index(self):
        return self.f_l

    def get_cct(self):
        return self.cc_t

    def plot_cri(self):
        ax = plt.subplot()
        ax.set_prop_cycle(cycler('color', ['#b3857f', '#a89061', '#939832', '#6ba375', '#609EA1', '#669bcb', '#9991c5',
                                           '#b989b1', '#FF0000', '#F1C131', '#00A800', '#21749c', '#F2D3E1', '#556b2f',
                                           '#000000']))  # '#E8B3A2',
        i = 0

        for key, c in self.colors.items():
            ax.bar(key, c)
            ax.annotate(round(c), (i - 0.3, round(c) + 0.4))
            i += 1
        plt.show()
        return ax

    def wavelength_to_rgb(self, w: float):
        round(w)
        red = 0.0
        green = 0.0
        blue = 0.0
        if 380 <= w < 440:
            red = -(w - 440) / (440 - 380)
            green = 0.0
            blue = 1.0
        if 440 <= w < 490:
            red = 0.0
            green = (w - 440) / (490 - 440)
            blue = 1.0
        if 490 <= w < 510:
            red = 0.0
            green = 1.0
            blue = -(w - 510) / (510 - 490)
        if 510 <= w < 580:
            red = (w - 510) / (580 - 510)
            green = 1.0
            blue = 0.0
        if 580 <= w < 645:
            red = 1.0
            green = -(w - 645) / (645 - 580)
            blue = 0.0
        if 645 <= w < 781:
            red = 1.0
            green = 0.0
            blue = 0.0

        factor = 0.0
        if 380 <= w < 420:
            factor = 0.3 + 0.7 * (w - 380) / (420 - 380)
        if 420 <= w < 701:
            factor = 1.0
        if 701 <= w < 781:
            factor = 0.3 + 0.7 * (780 - w) / (780 - 700)

        R = (red * factor)
        G = (green * factor)
        B = (blue * factor)
        return R, G, B

    def plot_spectrum(self):
        ax = plt.subplot()
        samples = np.mean(self.spectrum.intensity, axis=0)
        # rgb_indx = 0
        # d = 0.5
        # target = 0
        # start_color = list((255, 0, 247))
        for i in range(len(self.spectrum.wavelength)):
            # if start_color[rgb_indx] == target:
            #     rgb_indx = (rgb_indx + 1) % 3
            #     if start_color[rgb_indx] == 0:
            #         d = -2
            #         target = 255
            #     else:
            #         d = 0.5
            #         target = 0
            start_color = self.wavelength_to_rgb(self.spectrum.wavelength[i])
            ax.bar(self.spectrum.wavelength[i], samples[i],
                   color=(start_color[0], start_color[1], start_color[2]))
            # start_color[rgb_indx] = start_color[rgb_indx] - d
            # if start_color[rgb_indx] < 0:
            #     start_color[rgb_indx] = 0
            # if start_color[rgb_indx] > 255:
            #     start_color[rgb_indx] = 255
        plt.show()
        return ax

    def show(self):
        self.plot_spectrum()
        self.plot_cri()
        plt.show()
