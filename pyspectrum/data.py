import pickle
from dataclasses import dataclass, field

from numpy.typing import NDArray

from .errors import LoadError


@dataclass()
class Data:
    """Сырые данные, полученные со спектрометра"""
    intensity: NDArray[float]
    """Двумерный массив данных измерения. Первый индекс - номер кадра, второй - номер сэмпла в кадре"""
    clipped: NDArray[bool]
    """Массив boolean значений. Если `clipped[i,j]==True`, `intensity[i,j]` содержит зашкаленное значение"""
    exposure: int
    """Экспозиция в миллисекундах"""

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


@dataclass()
class Spectrum(Data):
    """Обработанные данные, полученные со спектрометра.
    Содержит в себе информацию о длинах волн измерения.
    В данный момент обработка заключается в вычитании темнового сигнала.
    """

    wavelength: NDArray[float]
    """длина волны фотоячейки"""
    number: NDArray[float] | None = field(default=None)  # номер фотоячейки TODO: not implemented

