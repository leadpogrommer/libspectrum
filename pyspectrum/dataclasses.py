import dataclasses

import numpy as np
from numpy.lib.npyio import NpzFile
from .errors import LoadError


@dataclasses.dataclass(repr=False)
class Data:
    """Сырые данные, полученные со спектрометра"""

    clipped: np.array
    """Массив boolean значений. Если `clipped[i]==True`, `amount[i]` содержит зашкаленное значение"""
    amount: np.array
    """Двумерный массив данных измерения. Первый индекс - номер кадра, второй - номер сэмпла в кадре"""

    @property
    def n_times(self) -> int:
        """Количество кадров"""
        return self.amount.shape[0]

    @property
    def n_amount(self) -> int:
        """Размерность кадра"""
        return self.amount.shape[1]

    @property
    def shape(self) -> tuple[int, int]:
        """Форма массива `amount`"""
        return self.amount.shape

    @staticmethod
    def _serializable_fields():
        return ['clipped', 'amount']

    def save(self, path: str):
        """
        Сохранить объект в файл
        :param path: Путь к файлу
        """
        with open(path, 'wb') as f:
            np.savez(f, **{field: self.__dict__[field] for field in self._serializable_fields()})

    @classmethod
    def load(cls, path: str) -> 'Data':
        """
        Прочитать объект из файла
        :param path: Путь к файлу
        :return: Загруженный объект
        """
        with np.load(path) as npz:
            if not isinstance(npz, NpzFile):
                raise LoadError(path)
            try:
                return cls(**{field: npz[field] for field in cls._serializable_fields()})
            except KeyError:
                raise LoadError(path)

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.n_times = }, {self.n_amount = })'


@dataclasses.dataclass(repr=False)
class Spectrum(Data):
    """
    Обработанные данные со спектрометра. Содержит в себе информацию о длинах волн измерения.
    В данный момент обработка заключается в вычитании темнового сигнала.
    """

    wavelength: np.array
    """Массив длин волн измерений"""

    @staticmethod
    def _serializable_fields():
        return ['clipped', 'amount', 'wavelength']
