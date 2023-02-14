import dataclasses
import json
import os.path

import _pyspectrum as internal
import numpy as np
from numpy.lib.npyio import NpzFile


class LoadError(Exception):
    def __int__(self, path: str):
        super().__init__(f'File {path} is not valid')


class SpectrumInfo():
    """
    Базовый класс для `Data` и `Spectrum`.
    """
    clipped: np.array
    samples: np.array

    @property
    def n_times(self) -> int:
        """Количество кадров"""
        return self.samples.shape[0]

    @property
    def n_samples(self) -> int:
        """Размерность кадра"""
        return self.samples.shape[1]

    @property
    def shape(self) -> tuple[int, int]:
        """Форма массива `samples`"""
        return self.samples.shape

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.n_times = }, {self.n_samples = })'


@dataclasses.dataclass(repr=False)
class Data(SpectrumInfo):
    """Сырые данные, полученные со спектрометра"""
    clipped: np.array
    """Массив boolean значений. Если `clipped[i]==True`, `samples[i]` содержит зашкаленное значение"""
    samples: np.array
    """Двумерный массив данных измерения. Первый индекс - номер кадра, второй - номер сэмпла в кадре"""

    def save(self, path: str):
        """
        Сохранить объект в файл
        :param path: Путь к файлу
        """
        with open(path, 'wb') as f:
            np.savez(f, clipped=self.clipped, samples=self.samples)

    @staticmethod
    def load(path: str) -> 'Data':
        """
        Прочитать объект из файла
        :param path: Путь к файлу
        :return: Загруженный объект
        """
        with np.load(path) as npz:
            if not isinstance(npz, NpzFile):
                raise LoadError(path)
            try:
                return Data(npz['clipped'], npz['samples'])
            except KeyError:
                raise LoadError(path)


@dataclasses.dataclass(repr=False)
class Spectrum(SpectrumInfo):
    """Обработанные данные со спектрометра. Содержит в себе информацию о длинах волн измерения"""
    clipped: np.array
    """Массив boolean значений. Если `clipped[i]==True`, `samples[i]` содержит зашкаленное значение"""
    samples: np.array
    """Двумерный массив данных измерения. Первый индекс - номер кадра, второй - номер сэмпла в кадре. Из данных вычтен темновой сигнал"""
    wavelength: np.array
    """Массив длин волн измерений"""

    def save(self, path: str):
        """
        Сохранить объект в файл
        :param path: Путь к файлу
        """
        with open(path, 'wb') as f:
            np.savez(f, clipped=self.clipped, samples=self.samples, wavelength=self.wavelength)

    @staticmethod
    def load(path: str) -> 'Spectrum':
        """
        Прочитать объект из файла
        :param path: Путь к файлу
        :return: Загруженный объект
        """
        with np.load(path) as npz:
            if not isinstance(npz, NpzFile):
                raise LoadError(path)
            try:
                return Spectrum(npz['clipped'], npz['samples'], npz['wavelength'])
            except KeyError:
                raise LoadError(path)


class Spectrometer:
    """Класс, представляющий высокоуровневую абстракцию над спектрометром"""
    device: internal.RawSpectrometer

    def __init__(self, device: internal.RawSpectrometer, pixel_start: int = 0, pixel_end: int = 4096,
                 pixel_reverse: bool = False,
                 dark_signal_path: str = 'dark_signal.dat'):
        """
        :param device: Низкоуровневый объект устройства. В данный момент может быть получен только через `usb_spectrometer`
        :param pixel_start: Номер первого значащего диода в линейке
        :param pixel_end: Номер последнего значащего диода в линейке
        :param pixel_reverse: Если True, порядок диодов будет обращён
        :param dark_signal_path: Путь к файлу темнового сигнала
        """
        self.device = device
        self.dark_signal = np.zeros((pixel_end - pixel_start))
        self.wavelengths = np.arange((pixel_end - pixel_start))
        self.pixel_start = pixel_start
        self.pixel_end = pixel_end
        self.pixel_reverse = -1 if pixel_reverse else 1
        self.dark_signal_path = dark_signal_path

    def read_dark_signal(self, n_times: int) -> None:
        """
        Считать темновой сигнал
        :param n_times: Количество кадров. В качестве темнового сигнала будет использоваться среднее значение для для каждого диода
        """
        data = self.read_raw_spectrum(n_times).samples
        self.dark_signal = np.mean(data, axis=0)

    def save_dark_signal(self):
        """Сохранить темновой сигнал на диск"""
        Data(np.zeros(self.dark_signal.shape[0]), self.dark_signal).save(self.dark_signal_path)

    def load_dark_signal(self):
        """Загрузить темновой сигнал с диска"""
        data = Data.load(self.dark_signal_path).samples
        if data.shape != self.dark_signal.shape:
            raise ValueError('Saved dark signal shape is different')
        self.dark_signal = data

    def load_or_read_and_save_dark_signal(self, n_times) -> bool:
        """
        Если файл темнового сигнала существует, загрузить его. Иначе, считать темновой сигнал и сохранить его в файл
        :param n_times: Количество кадров
        :return: True, если сигнал был считан с устройства
        """
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
        """
        Загрузить данные профилирования
        :param path: Путь к файлу данных профилирования
        """
        # TODO: validate data
        with open(path, 'r') as file:
            data = json.load(file)
        wavelengths = np.array(data['wavelengths'], dtype=float)
        if len(wavelengths) != (self.pixel_end - self.pixel_start):
            raise ValueError("Profiling data has incorrect number of pixels")
        self.wavelengths = wavelengths

    def read_raw_spectrum(self, n_times: int) -> Data:
        """Считать сырой спектр с устройства

        :param n_times: Количество кадров
        :return: Полученные данные без предварительной обработки
        """
        data = self.device.readFrame(n_times)  # type: internal.RawSpectrum
        samples = data.samples[:, self.pixel_start:self.pixel_end][:, ::self.pixel_reverse]
        clipped = data.clipped[:, self.pixel_start:self.pixel_end][:, ::self.pixel_reverse]
        return Data(clipped, samples)

    def read_spectrum(self, n_times: int) -> Spectrum:
        """Получить данные с устройства

        :param n_times: Количество кадров
        :return: Полученные данные
        """
        data = self.read_raw_spectrum(n_times)
        return Spectrum(data.clipped, data.samples - self.dark_signal, self.wavelengths)

    def set_timer(self, millis: int) -> None:
        """Установить время экспозиции
        :param millis: Время экспозиции в миллисекундах
        """
        self.device.setTimer(millis)


def usb_spectrometer(vid: int, pid: int) -> internal.UsbRawSpectrometer:
    """Create usb spectrometer for Spectrometer creation
    :param vid: Usb vendor id
    :param pid: Usb product id
    :return: Device object needed for Spectrometer creation
    """
    return internal.UsbRawSpectrometer(vid, pid)
