import dataclasses

import numpy as np
from .errors import LoadError
import pickle


@dataclasses.dataclass(repr=False)
class Data:
    """Сырые данные, полученные со спектрометра"""
    clipped: np.array
    """Массив boolean значений. Если `clipped[i]==True`, `amount[i]` содержит зашкаленное значение"""
    amount: np.array
    """Двумерный массив данных измерения. Первый индекс - номер кадра, второй - номер сэмпла в кадре"""
    exposure: int
    """Экспозиция (в миллисекундах), с которой были сделаны измерения"""

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

    def save(self, path: str):
        """
        Сохранить объект в файл
        :param path: Путь к файлу
        """
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str):
        """
        Прочитать объект из файла
        :param path: Путь к файлу
        :return: Загруженный объект
        """
        with open(path, 'rb') as f:
            result = pickle.load(f)
            if not isinstance(result, cls):
                raise LoadError(path)
            return result

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
