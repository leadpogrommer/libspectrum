import string
import time
from typing import Any
from os import path
import pickle
from pyspectrum import Spectrum


class FileSpectrometer():
    _data = None

    class CustomUnpickler(pickle.Unpickler):
        def find_class(self, __module_name: str, __global_name: str) -> Any:
            if __global_name == 'Spectrum':
                return Spectrum
            return super().find_class(__module_name, __global_name)

    def __init__(self, filename: string) -> None:
        self.__creation_time = time.time()
        self._data = self.CustomUnpickler(open(path.join(path.dirname(path.realpath(__file__)), filename), 'rb')).load()

    def read_spectrum(self, n_times: int) -> Spectrum:
        t = time.time()
        d = int(((t - self.__creation_time) / 2) * 10) % len(self._data)
        return self._data[d]
