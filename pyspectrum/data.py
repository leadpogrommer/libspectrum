
import pickle
from dataclasses import dataclass

from numpy.typing import NDArray

from .errors import LoadError


@dataclass(frozen=True)
class Data:
    """Сырые данные, полученные со спектрометра"""
    amount: NDArray[float]  # выходное значение фотоячейки
    clipped: NDArray[bool]  # зашкал фотоячейки
    exposure: int  # in ms

    @property
    def n_times(self) -> int:
        """Количество измерений"""
        return self.amount.shape[0]

    @property
    def n_amounts(self) -> int:
        """Количество отсчетов"""
        return self.amount.shape[1]

    @property
    def shape(self) -> tuple[int, int]:
        """Размерность данынх"""
        return self.amount.shape

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
        return f'{cls.__name__}({self.n_times = }, {self.n_amounts = })'


@dataclass(repr=False)
class Spectrum(Data):
    """Обработанные данные, полученные со спектрометра.
    Содержит в себе информацию о длинах волн измерения.
    В данный момент обработка заключается в вычитании темнового сигнала.
    """

    wavelength: NDArray[float]  # длина волны фотоячейки
