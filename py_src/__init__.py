import dataclasses
import json
import os.path

import _pyspectrum as internal
import numpy as np


class SpectrumInfo(object):
    clipped: np.array
    samples: np.array

    @property
    def n_times(self) -> int:
        return self.samples.shape[0]

    @property
    def n_samples(self) -> int:
        return self.samples.shape[1]

    @property
    def shape(self) -> tuple[int, int]:
        return self.samples.shape

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.n_times = }, {self.n_samples = })'


@dataclasses.dataclass(repr=False)
class Data(SpectrumInfo):
    clipped: np.array
    samples: np.array


@dataclasses.dataclass(repr=False)
class Spectrum(SpectrumInfo):
    clipped: np.array
    samples: np.array
    wavelength: np.array


class Spectrometer:
    device: internal.RawSpectrometer

    def __init__(self, device: internal.RawSpectrometer, pixel_start=0, pixel_end=4096, pixel_reverse=False,
                 dark_signal_path=None):
        self.device = device
        self.dark_signal = np.zeros((pixel_end - pixel_start))
        self.wavelengths = np.arange((pixel_end - pixel_start))
        self.pixel_start = pixel_start
        self.pixel_end = pixel_end
        self.pixel_reverse = -1 if pixel_reverse else 1
        if dark_signal_path is None:
            self.dark_signal_path = 'dark_signal.dat'
        else:
            self.dark_signal_path = dark_signal_path

    def read_dark_signal(self, n_times: int) -> None:
        data = self.read_raw_spectrum(n_times).samples
        self.dark_signal = np.mean(data, axis=0)

    def save_dark_signal(self):
        self.dark_signal.tofile(self.dark_signal_path, sep=',')

    def load_dark_signal(self):
        data = np.fromfile(self.dark_signal_path, float, sep=',')
        if data.shape != self.dark_signal.shape:
            raise ValueError('Save dark signal shape is different')
        self.dark_signal = data

    def load_or_read_and_save_dark_signal(self, n_times) -> bool:
        if os.path.isfile(self.dark_signal_path):
            try:
                self.load_dark_signal()
                return False
            except ValueError:
                pass
        self.read_dark_signal(n_times)
        self.save_dark_signal()
        return True

    def load_calibration_data(self, path: str) -> None:
        # TODO: validate data
        with open(path, 'r') as file:
            data = json.load(file)
        wavelengths = np.array(data['wavelengths'], dtype=float)
        if len(wavelengths) != (self.pixel_end - self.pixel_start):
            raise ValueError("Profiling data has incorrect number of pixels")
        self.wavelengths = wavelengths

    def read_raw_spectrum(self, n_times: int):
        data = self.device.readFrame(n_times)  # type: internal.RawSpectrum
        samples = data.samples[:, self.pixel_start:self.pixel_end][:, ::self.pixel_reverse]
        clipped = data.clipped[:, self.pixel_start:self.pixel_end][:, ::self.pixel_reverse]
        return Data(clipped, samples)

    def read_spectrum(self, n_times: int) -> Spectrum:
        data = self.read_raw_spectrum(n_times)
        return Spectrum(data.clipped, data.samples - self.dark_signal, self.wavelengths)

    def set_timer(self, millis: int) -> None:
        self.device.setTimer(millis)


def usb_spectrometer(vid: int, pid: int) -> internal.UsbRawSpectrometer:
    return internal.UsbRawSpectrometer(vid, pid)
