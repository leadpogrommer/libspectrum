
import pickle
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .errors import LoadError


@dataclass(frozen=True)
class Data:
    """Сырые данные, полученные со спектрометра"""
    intensity: NDArray[float]  # выходное значение фотоячейки
    clipped: NDArray[bool]  # зашкал фотоячейки
    exposure: int  # in ms

    @property
    def n_times(self) -> int:
        """Количество измерений"""
        return self.intensity.shape[0]

    @property
    def n_numbers(self) -> int:
        """Количество отсчетов"""
        return self.intensity.shape[1]

    @property
    def shape(self) -> tuple[int, int]:
        """Размерность данынх"""
        return self.intensity.shape

    def save(self, path: str):
        """Сохранить объект в файл"""
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str) -> 'Data':
        """Прочитать объект из файла"""

        with open(path, 'rb') as f:
            result = pickle.load(f)

        if not isinstance(result, cls):
            raise LoadError(path)

        return result

    def __repr__(self) -> str:
        cls = self.__class__
        return f'{cls.__name__}({self.n_times = }, {self.n_numbers = })'


@dataclass(repr=False)
class Spectrum(Data):
    """Обработанные данные, полученные со спектрометра.
    Содержит в себе информацию о длинах волн измерения.
    В данный момент обработка заключается в вычитании темнового сигнала.
    """

    wavelength: NDArray[float]  # длина волны фотоячейки
    _number: NDArray[int] | None = field(default=None)

    @property
    def time(self):
        return np.arange(self.n_times)

    @property
    def index(self):
        '''индекс фотоячейки'''
        return np.arange(self.n_numbers)

    @property
    def number(self):
        '''номер фотоячейки'''
        if self._number is None:
            self._number = self.index

        return self._number

    def __getitem__(self, index):
        raise NotImplementedError

    def __add__(self, other: float | NDArray[float] | 'Spectrum'):
        raise NotImplementedError

    def __sub__(self, other: float | NDArray[float] | 'Spectrum'):
        raise NotImplementedError
