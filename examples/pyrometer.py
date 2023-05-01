# This file contains Pyrometer class for pyrometer notebook
from numpy.typing import NDArray
from math import log
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
import scipy.stats

from pyspectrum import Spectrum

c2 = 14_388 * 1000

# TODO: calculate error
class Pyrometer:
    def __init__(self, calibration_spectrum: Spectrum, calibration_temp: float) -> None:
        self.temp = calibration_temp
        self.calibration = calibration_spectrum
        # run results
        self.temperatures = None
        self.deltas = None
        self.input_data = None
        self.xmin = None
        self.xmax = None
        self.wien_x = None
        self.wien_y = None
        self.line_m = None
        self.line_c = None

    def _convert_to_wien(self, y: NDArray, x: NDArray):
        ry = np.zeros(y.shape, y.dtype)
        rx = np.zeros(x.shape, x.dtype)
        for i in range(y.shape[0]):
            rx[i] = c2/x[i]
            ry[i] = log((x[i]**4) * y[i])
        return ry[::-1], rx[::-1]
    
    def _get_e(self, wl, intensity, t):
        ys, xs = self._convert_to_wien(intensity, wl)
        return np.vectorize(lambda x,y: -x/t - y)(xs, ys)
    
    def _get_temp(self, wl, intensity, xmin, xmax):
        es = self._get_e(self.calibration.wavelength, self.calibration.intensity[-1], self.temp)

        intensity[intensity <=0] = 0.1 # without this log freaks out on noisy negative values
        ry, rx = self._convert_to_wien(intensity, wl)
        ry = ry + es

        self.wien_y = ry
        self.wien_x = rx


        converted = np.stack([rx, ry], axis=0).T
        imin = (np.abs(converted.T[0] - xmin)).argmin()
        imax = (np.abs(converted.T[0] - xmax)).argmin()
        cropped = converted[imin:imax]

        A = np.vstack([cropped.T[0], np.ones(cropped.shape[0])]).T
        m, c = np.linalg.lstsq(A, cropped.T[1], rcond=None)[0]
        self.line_c = c
        self.line_m = m
        
        temperature = -1/m

        # error calculation
        xs = cropped.T[0]
        ys = cropped.T[1]

        ei2 = (ys - (xs*m + c))**2
        s2 = (1/(len(intensity)-2))*ei2.sum()
        Db = s2/( (xs - xs.mean())**2 ).sum()
        # display(Db)

        deltaM = scipy.stats.t.interval(0.95, df=len(intensity)-2)[1]*(Db**0.5)

        deltaT = deltaM/(m**2)

        return np.array([temperature, deltaT])
    
    def run(self, spectrum: Spectrum, wl_min: float, wl_max: float) -> NDArray:
        self.input_data = spectrum
        xmax = c2/wl_min
        xmin = c2/wl_max
        self.xmax = xmax
        self.xmin = xmin
        self.temperatures, self.deltas = np.apply_along_axis(lambda a: self._get_temp(spectrum.wavelength, a, xmin, xmax), 1, spectrum.intensity).T

        # fill result fields with data from last measurement
        self._get_temp(spectrum.wavelength, spectrum.intensity[-1], xmin, xmax)

    def show(self, filename: None|str =None):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8*2, 6*2))
        xmin, xmax = self.xmin, self.xmax

        ax1.fill_between(np.arange(len(self.temperatures)), self.temperatures - self.deltas, self.temperatures + self.deltas, color='red')
        ax1.plot(self.temperatures)
        ax1.set_ylabel('temperature')
        ax1.set_xlabel('measurement')
        
        ax2.set_title('Spectrum (last measurement)')
        ax2.set_ylabel('intensity')
        ax2.set_xlabel('λ, нм')
        ax2.plot(self.input_data.wavelength, self.input_data.intensity[-1])
        ax2.vlines([c2/self.xmin, c2/self.xmax], ymin=self.input_data.intensity[-1].min(), ymax=self.input_data.intensity[-1].max())

        ax3.set_title('Last spectrum in wien coordinates')
        ax3.set_xlabel('C2/λi')
        ax3.set_ylabel('ln(λi^4 * Ni)')
        ax3.plot(self.wien_x, self.wien_y)
        ax3.vlines([self.xmin, self.xmax], ymin=np.min(self.wien_y), ymax=np.max(self.wien_y))


        ax4.set_title('Last spectrum in wien coordinates (close-up)')
        ax4.set_xlabel('C2/λi')
        ax4.set_ylabel('ln(λi^4 * Ni)')

        imin = (np.abs(self.wien_x - xmin)).argmin()
        imax = (np.abs(self.wien_x - xmax)).argmin()

        ax4.plot(self.wien_x[imin:imax], self.wien_y[imin:imax])
        ax4.set_xlim((self.wien_x[imin], self.wien_x[imax]))
        ax4.set_ylim((self.wien_y[imin:imax].min(), self.wien_y[imin:imax].max()))
        ax4.plot(self.wien_x, self.wien_x*self.line_m + self.line_c)

        if filename is not None:
            fig.savefig(filename)

    def get_temperature(self):
        return np.array([self.temperatures, self.deltas]).T


