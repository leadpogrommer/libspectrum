import _pyspectrum as internal
import dataclasses
import numpy as np
import json


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
        return  f'{type(self).__name__}({self.n_times = }, {self.n_samples = })'


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

    def __init__(self, device: internal.RawSpectrometer, pixel_start=2050, pixel_end=2050+1800, pixel_reverse=True):
        self.device = device
        self.dark_signal = np.zeros((pixel_end - pixel_start))
        self.wavelengths = np.arange((pixel_end - pixel_start))
        self.pixel_start = pixel_start
        self.pixel_end = pixel_end
        self.pixel_reverse = -1 if pixel_reverse else 1

    def read_dark_signal(self, n_times: int) -> None:
        data = self.read_raw_spectrum(n_times).samples
        self.dark_signal = np.mean(data, axis=0)

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
