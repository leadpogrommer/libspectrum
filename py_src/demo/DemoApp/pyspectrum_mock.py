import dataclasses
import string
import time
from typing import Any
import numpy as np
from os import path
import pickle



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
class Spectrum(SpectrumInfo):
    clipped: np.array
    samples: np.array
    wavelength: np.array


class CustomUnpickler(pickle.Unpickler):
    def find_class(self, __module_name: str, __global_name: str) -> Any:
        if __global_name == 'Spectrum':
            return Spectrum
        return super().find_class(__module_name, __global_name)




def __not_implemented(self):
        raise NotImplementedError('Not implemented in mock')

class Spectrometer:
    _data = None
    def __init__(self,filename: string) -> None:
        self.__creation_time = time.time()
        self._data = CustomUnpickler(open(path.join(path.dirname(path.realpath(__file__)), filename), 'rb')).load()
    def read_dark_signal(self, n_times: int):
        pass

    def load_calibration_data(self, path: str):
        pass

    def read_raw_spectrum(self, n_times: int):
        __not_implemented()

    def read_spectrum(self, n_times: int) -> Spectrum:
        if n_times != 1:
            __not_implemented('Only n_times=1 supported in mock')
        t = time.time()
        d = int(((t - self.__creation_time)/2)*10) % len(self._data)
        return self._data[d]

    def read_sepctre(self, module: int):
        return self._data[module]
