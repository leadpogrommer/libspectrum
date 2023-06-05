import numpy as np
from pyspectrum import Spectrum

import colorimeter_data as data

class Colorimeter:
    def __init__(self, reference_spectrum: Spectrum, illuminant: str='E', observer: str='2deg'):
        self.reference_spectrum = reference_spectrum
        self.illuminant = illuminant
        self.observer = observer

    def _rgb_space_matrix(self, rgb_space: str):
        [[xr, yr], [xg, yg], [xb, yb]] = data.RGB_PRIMARIES[rgb_space]
        w = data.RGB_WHITE_POINT[rgb_space][self.observer]
        m1 = np.matrix([[xr/yr, xg/yg, xb/yb], [1, 1, 1], [(1 - xr - yr)/yr, (1 - xg - yg)/yg, (1 - xb - yb)/yb]])
        m = m1 * np.diag((m1.I * np.matrix(w).T).A1)
        return m.I

    def _adaptation_matrix(self, rgb_space: str, adaptation_method: str):
        w_src = data.ILLUMINANT_WHITE_POINT[self.illuminant][self.observer]
        w_dst = data.RGB_WHITE_POINT[rgb_space][self.observer]
        m1 = data.CHROMATIC_ADAPTATION_MATRIX[adaptation_method]
        s = (m1 * np.matrix(w_src).T).A1
        d = (m1 * np.matrix(w_dst).T).A1
        m = m1.I * np.diag(d / s) * m1
        return m

    def measure(self, spectrum: Spectrum):
        illuminant_data = data.ILLUMINANT_INTENSITY[self.illuminant]
        observer_data = data.OBSERVER_SENSITIVITY[self.observer]

        ind = [illuminant_data['wavelength'][0] <= x <= illuminant_data['wavelength'][-1] for x in spectrum.wavelength]
        wl = spectrum.wavelength[ind]
        dwl = np.diff(spectrum.wavelength, append=0)[ind]
        intensity = (spectrum.intensity[-1] / self.reference_spectrum.intensity[-1].clip(0.1))[ind]

        sens_x = np.interp(wl, observer_data['wavelength'], observer_data['X'])
        sens_y = np.interp(wl, observer_data['wavelength'], observer_data['Y'])
        sens_z = np.interp(wl, observer_data['wavelength'], observer_data['Z'])

        illuminant_intensity = np.interp(wl, illuminant_data['wavelength'], illuminant_data['intensity'])

        k = 1 / max(np.sum(sens_y * illuminant_intensity * dwl), 0.1)
        X = k * np.sum(sens_x * intensity * illuminant_intensity * dwl)
        Y = k * np.sum(sens_y * intensity * illuminant_intensity * dwl)
        Z = k * np.sum(sens_z * intensity * illuminant_intensity * dwl)
        self._XYZ = np.array([X, Y, Z])

    def XYZ(self):
        return np.copy(self._XYZ)

    def xyY(self):
        X, Y, Z = self._XYZ
        return np.array([X / (X + Y + Z), Y / (X + Y + Z), Y])

    def RGB(self, rgb_space: str='sRGB', adaptation_method: str | None='Bradford'):
        m_adapt = self._adaptation_matrix(rgb_space, adaptation_method) if adaptation_method is not None else 1
        m = self._rgb_space_matrix(rgb_space)
        v = (m * m_adapt * np.matrix(self._XYZ).T).A1
        return np.vectorize(data.RGB_GAMMA[rgb_space])(np.clip(v, 0, 1))

    def Lab(self):
        w = data.ILLUMINANT_WHITE_POINT[self.illuminant][self.observer]
        fx, fy, fz = np.vectorize(lambda x: x ** (1/3) if x > 0.008856 else (903.3 * x + 16) / 116)(self._XYZ / w)
        return np.array([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)])

    def LCh_ab(self):
        L, a, b = self.Lab()
        C = (a**2 + b**2) ** 0.5
        h = np.arctan2(b, a) * 180 / np.pi
        return np.array([L, C, h])

    def Luv(self):
        X, Y, Z = self._XYZ
        wx, wy, wz = data.ILLUMINANT_WHITE_POINT[self.illuminant][self.observer]
        L = 116 * Y ** (1/3) - 16 if Y > 0.008856 else 903.3 * Y
        u = 13 * L * (4 * X / (X + 15 * Y + 3 * Z) - 4 * wx / (wx + 15 * wy + 3 * wz))
        v = 13 * L * (9 * Y / (X + 15 * Y + 3 * Z) - 9 * wy / (wx + 15 * wy + 3 * wz))
        return np.array([L, u, v])

    def LCh_uv(self):
        L, u, v = self.Luv()
        C = (u**2 + v**2) ** 0.5
        h = np.arctan2(v, u) * 180 / np.pi
        return np.array([L, C, h])
