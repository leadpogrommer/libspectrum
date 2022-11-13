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

    def __init__(self, device: internal.RawSpectrometer):
        self.device = device
        self.dark_signal = np.zeros((self.device.getPixelCount()))
        self.wavelengths = np.arange(device.getPixelCount())
        self.led_map = np.arange(device.getPixelCount())

    def read_dark_signal(self, n_times: int) -> None:
        data = self.device.readFrame(n_times).samples
        self.dark_signal = np.mean(data, axis=0)

    def load_calibration_data(self, path: str) -> None:
        # TODO: validate data
        with open(path, 'r') as file:
            data = json.load(file)
        self.wavelengths = np.array(data['wavelengths'], dtype=float)
        self.led_map = np.array(data['leds'], dtype=int)

    def read_raw_spectrum(self, n_times: int) -> Data:
        # TODO: test destructor
        data = self.device.readFrame(n_times)  # type: internal.RawSpectrum
        return Data(data.clipped, data.samples)

    def read_spectrum(self, n_times: int) -> Spectrum:
        data = self.device.readFrame(n_times)  # type: internal.RawSpectrum
        samples = (data.samples - self.dark_signal)[:,self.led_map]
        clipped = data.clipped[:,self.led_map]
        return Spectrum(clipped, samples, self.wavelengths)

    def set_timer(self, millis: int) -> None:
        self.device.setTimer(millis)


def usb_spectrometer(vid: int, pid: int) -> internal.UsbRawSpectrometer:
    return internal.UsbRawSpectrometer(vid, pid)
