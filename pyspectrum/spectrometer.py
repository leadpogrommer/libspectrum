import dataclasses
import json
from typing import Optional

import _pyspectrum as internal
import numpy as np
from numpy.typing import NDArray

from . import LoadError
from .dataclasses import Data, Spectrum
from .errors import ConfigurationError
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


@dataclasses.dataclass()
class FactoryConfig:
    start: int
    end: int
    reverse: bool

    @staticmethod
    def load(path: str) -> 'FactoryConfig':
        with open(path, 'r') as f:
            json_data = json.load(f)
        try:
            return FactoryConfig(int(json_data['start']), int(json_data['end']), bool(json_data['reverse']))
        except KeyError:
            raise LoadError(path)


class Spectrometer:
    """Класс, представляющий высокоуровневую абстракцию над спектрометром"""
    __device: internal.RawSpectrometer
    __dark_signal_path: str | None = None
    __dark_signal: Data | None = None
    __wavelengths: NDArray[float] | None = None
    __config: FactoryConfig
    __exposure: int = 10
    __n_frames: int = 1

    def __init__(self, device: internal.RawSpectrometer, factory_config_path: str = 'factory_config.json'):
        """
        :param device: Низкоуровневый объект устройства. В данный момент может быть получен только через
        `usb_spectrometer`
        :param factory_config_path: Путь к файлу заводских настроек
        """
        self.__device = device
        self.__config = FactoryConfig.load(factory_config_path)
        self.__device.setTimer(self.__exposure)

    def read_dark_signal(self, n_times: int) -> None:
        """
        Считать темновой сигнал
        :param n_times: Количество кадров.
        В качестве темнового сигнала будет использоваться среднее значение для для каждого диода
        """
        self.__dark_signal = self.__read_raw(n_times)

    def save_dark_signal(self):
        """Сохранить темновой сигнал на диск"""
        if self.__dark_signal_path is None:
            raise ConfigurationError('Dark signal path is not set')
        if self.__dark_signal is None:
            raise ConfigurationError('Dark signal is not loaded')
        self.__dark_signal.save(self.__dark_signal_path)

    def read_raw(self) -> Data:
        """Считать сырой спектр с устройства

        :return: Полученные данные без предварительной обработки
        """
        return self.__read_raw(self.__n_frames)

    def __read_raw(self, n_times):
        direction = -1 if self.__config.reverse else 1
        data = self.__device.readFrame(n_times)  # type: internal.RawSpectrum
        amount = data.samples[:, self.__config.start:self.__config.end][:, ::direction]
        clipped = data.clipped[:, self.__config.start:self.__config.end][:, ::direction]
        return Data(clipped, amount, self.__exposure)

    def read(self) -> Spectrum:
        """Получить данные с устройства.
        Если данные профилирования или темновой сигнал не были загружены, поднимает Exception.

        :return: Полученные обработанные данные (содержат в себе данные профилирования)
        """
        if self.__wavelengths is None:
            raise ConfigurationError('Profile data is not loaded')
        if self.__dark_signal is None:
            raise ConfigurationError('Dark signal is not loaded')
        data = self.read_raw()
        return Spectrum(data.clipped, data.amount - np.mean(self.__dark_signal.amount, axis=0), self.__exposure, self.__wavelengths)

    def fully_configured(self) -> bool:
        """Возвращает `True`, если спектрометр сконфигурирован для чтения обработанных данных"""
        return (self.__dark_signal is not None) and (self.__wavelengths is not None)

    def set_config(self,
                   exposure: Optional[int] = None,
                   n_times: Optional[int] = None,
                   dark_signal_path: Optional[str] = None,
                   profile_path: Optional[str] = None,
                   ):
        """Изменить различные настройки спектрометра. Все параметры опциональны, при
        отсутствии параметра соответствующая настройка не изменяется.

        :param exposure: Экспозиция в миллисекундах. При изменении темновой сигнал будет сброшен.
        :param n_times: Количество кадров, которое будет записываться методам `read` и `rea_raw`
        :param dark_signal_path: Путь к файлу темнового сигнала. Если файл темнового сигнала существует и валиден,
        он будет загружен.
        :param profile_path: Путь к файлу данных профилирования
        """
        if exposure is not None and exposure != self.__exposure:
            self.__exposure = exposure
            self.__device.setTimer(self.__exposure)
            if self.__dark_signal is not None:
                self.__dark_signal = None
                eprint('Different exposure was set, dark signal invalidated')
        if n_times is not None:
            self.__n_frames = n_times
        if dark_signal_path is not None:
            self.__dark_signal_path = dark_signal_path
            self.__load_dark_signal()
        if profile_path is not None:
            self.__load_calibration_data(profile_path)

    def __load_dark_signal(self):
        try:
            data = Data.load(self.__dark_signal_path)
        except Exception:
            eprint('Dark signal file is invalid or does not exist, dark signal was NOT loaded')
            return
        if data.shape != self.__dark_signal.shape:
            eprint("Saved dark signal has different shape, dark signal was NOT loaded")
            return
        if data.exposure != self.__exposure:
            eprint('Saved dark signal has different exposure, dark signal was NOT loaded')
            return
        self.__dark_signal = data
        eprint('Dark signal loaded')

    def __load_calibration_data(self, path: str) -> None:
        with open(path, 'r') as file:
            data = json.load(file)
        wavelengths = np.array(data['wavelengths'], dtype=float)
        if len(wavelengths) != (self.__config.end - self.__config.start):
            raise ValueError("Profiling data has incorrect number of pixels")
        self.__wavelengths = wavelengths


def usb_spectrometer(vid: int = 0x0403, pid: int = 0x6014) -> internal.UsbRawSpectrometer:
    """Create usb spectrometer for Spectrometer creation
    :param vid: Usb vendor id
    :param pid: Usb product id
    :return: Device object needed for Spectrometer creation
    """
    return internal.UsbRawSpectrometer(vid, pid)
