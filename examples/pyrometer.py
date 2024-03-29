# This file contains Pyrometer class for pyrometer notebook
from numpy.typing import NDArray
from math import log
import numpy as np
from IPython.display import display
import matplotlib.pyplot as plt
import scipy.stats
from typing import TypeAlias

Nanometers: TypeAlias = float
Kelvin: TypeAlias = float

from pyspectrum import Spectrum

c2 = 14_388 * 1000

# TODO: calculate error
class Pyrometer:
    def __init__(self, calibration_spectrum: Spectrum, calibration_temp: Kelvin) -> None:
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
    
    def run(self, spectrum: Spectrum, wavelength_range: tuple[Nanometers, Nanometers]) -> None:
        self.input_data = spectrum
        xmax = c2/wavelength_range[0]
        xmin = c2/wavelength_range[1]
        self.xmax = xmax
        self.xmin = xmin
        self.temperatures, self.deltas = np.apply_along_axis(lambda a: self._get_temp(spectrum.wavelength, a, xmin, xmax), 1, spectrum.intensity).T

        # fill result fields with data from last measurement
        self._get_temp(spectrum.wavelength, spectrum.intensity[-1], xmin, xmax)

    def show(self, filename: None|str =None):
        fig, ((ax1, ax5), (ax2, ax3), (ax4, ax6)) = plt.subplots(3, 2, figsize=(8*2, 6*3))
        xmin, xmax = self.xmin, self.xmax

        # ax1.fill_between(np.arange(len(self.temperatures)), self.temperatures - self.deltas, self.temperatures + self.deltas, color='red')
        ax1.plot(self.temperatures)
        ax1.set_title('График температуры')
        ax1.set_ylabel('Температура, $K$')
        ax1.set_xlabel('Номер измерения')

        ax5.plot(self.deltas)
        ax5.set_title('График погрешности')
        ax5.set_ylabel('Погрешность, $K$')
        ax5.set_xlabel('Номер измерения')

        
        ax2.set_title('Спектр (последнее измерение)')
        ax2.set_ylabel('Интенсивность')
        ax2.set_xlabel(r'$\lambda$, нм')
        ax2.plot(self.input_data.wavelength, self.input_data.intensity[-1])
        ax2.vlines([c2/self.xmin, c2/self.xmax], ymin=self.input_data.intensity[-1].min(), ymax=self.input_data.intensity[-1].max())

        ax3.set_title('Последний спектр в координатах Вина')
        ax3.set_xlabel(r'$C_2/\lambda_i, K$')
        ax3.set_ylabel(r'$ln(\lambda_i^4 * N_i)$')
        ax3.plot(self.wien_x, self.wien_y)
        ax3.vlines([self.xmin, self.xmax], ymin=np.min(self.wien_y), ymax=np.max(self.wien_y))


        ax4.set_title('Последний спектр в координатах Вина (Ближе)')
        ax4.set_xlabel(r'$C_2/\lambda_i, K$')
        ax4.set_ylabel(r'$ln(\lambda_i^4 * N_i)$')

        imin = (np.abs(self.wien_x - xmin)).argmin()
        imax = (np.abs(self.wien_x - xmax)).argmin()

        ax4.plot(self.wien_x[imin:imax], self.wien_y[imin:imax])
        ax4.set_xlim((self.wien_x[imin], self.wien_x[imax]))
        ax4.set_ylim((self.wien_y[imin:imax].min(), self.wien_y[imin:imax].max()))
        ax4.plot(self.wien_x, self.wien_x*self.line_m + self.line_c)

        ax6.set_title('Последний спектр в координатах Вина - аппрокс. прямая')
        ax6.set_xlabel(r'$C_2/\lambda_i, K$')
        ax6.set_ylabel(r'$ln(\lambda_i^4 * N_i)$')
        ax6.plot(self.wien_x, self.wien_y - (self.wien_x*self.line_m + self.line_c))

        if filename is not None:
            fig.savefig(filename)

    def get_temperature(self) -> NDArray[np.float_]:
        """Get temperature in Kelvin"""
        return self.temperatures
    
    def get_deviation(self) -> NDArray[np.float_]:
        """Get temperature deviation in Kelvin"""
        return self.deltas


