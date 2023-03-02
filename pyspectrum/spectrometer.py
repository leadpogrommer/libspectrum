import json
import sys
from dataclasses import dataclass
from typing import Optional

import _pyspectrum as internal
import numpy as np
from numpy.typing import NDArray

from .data import Data, Spectrum
from .errors import ConfigurationError, LoadError


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


@dataclass(frozen=True)
class FactoryConfig:
    start: int
    end: int
    reverse: bool

    @staticmethod
    def load(path: str) -> 'FactoryConfig':
        try:
            with open(path, 'r') as f:
                json_data = json.load(f)
            return FactoryConfig(int(json_data['start']), int(json_data['end']), bool(json_data['reverse']))

        except KeyError:
            raise LoadError(path)


@dataclass(frozen=False)
class Config:
    exposure: int = 10  # время экспозиции, ms
    n_times: int = 1  # количество измерений


class Spectrometer:
    """Класс, представляющий высокоуровневую абстракцию над спектрометром"""
    __device: internal.RawSpectrometer
    __dark_signal_path: str | None = None
    __dark_signal: Data | None = None
    __wavelengths: NDArray[float] | None = None
    __factory_config: FactoryConfig
    __config: Config

    def __init__(self, device: internal.RawSpectrometer, factory_config_path: str = 'factory_config.json'):
        """
        Params:
            device: Низкоуровневый объект устройства. В данный момент может быть получен только через `usb_spectrometer`
            factory_config_path: Путь к файлу заводских настроек
        """
        self.__device = device
        self.__factory_config = FactoryConfig.load(factory_config_path)
        self.__config = Config()
        self.__device.setTimer(self.__config.exposure)

    # --------        dark signal        --------
    def __load_dark_signal(self):
        try:
            data = Data.load(self.__dark_signal_path)
        except Exception:
            eprint('Dark signal file is invalid or does not exist, dark signal was NOT loaded')
            return

        if data.shape != self.__dark_signal.shape:
            eprint("Saved dark signal has different shape, dark signal was NOT loaded")
            return
        if data.exposure != self.__config.exposure:
            eprint('Saved dark signal has different exposure, dark signal was NOT loaded')
            return

        self.__dark_signal = data
        eprint('Dark signal loaded')

    def read_dark_signal(self, n_times: Optional[int] = None) -> None:
        """Считать темновой сигнал"""
        self.__dark_signal = self.read_raw(n_times)

    def save_dark_signal(self):
        """Сохранить темновой сигнал"""
        if self.__dark_signal_path is None:
            raise ConfigurationError('Dark signal path is not set')
        if self.__dark_signal is None:
            raise ConfigurationError('Dark signal is not loaded')

        self.__dark_signal.save(self.__dark_signal_path)

    # --------        wavelength calibration        --------
    def __load_wavelength_calibration(self, path: str) -> None:
        factory_config = self.__factory_config

        with open(path, 'r') as file:
            data = json.load(file)

        wavelengths = np.array(data['wavelengths'], dtype=float)
        if len(wavelengths) != (factory_config.end - factory_config.start):
            raise ValueError("Wavelength calibration data has incorrect number of pixels")

        self.__wavelengths = wavelengths
        eprint('Wavelength calibration loaded')

    # --------        read raw        --------
    def read_raw(self, n_times: Optional[int] = None) -> Data:
        """
        Получить сырые данные с устройства
        Returns:
            Сырые данные, полученные с устройства

        """
        device = self.__device
        factory_config = self.__factory_config
        config = self.__config

        direction = -1 if factory_config.reverse else 1
        n_times = config.n_times if n_times is None else n_times

        data = device.readFrame(n_times)  # type: internal.RawSpectrum
        intensity = data.samples[:, factory_config.start:factory_config.end][:, ::direction]
        clipped = data.clipped[:, factory_config.start:factory_config.end][:, ::direction]

        return Data(
            intensity=intensity,
            clipped=clipped,
            exposure=config.exposure,
        )

    # --------        read        --------
    def read(self) -> Spectrum:
        """
       Получить обработанный спектр с устройства
       Returns:
           Считанный спектр

       """
        if self.__wavelengths is None:
            raise ConfigurationError('Wavelength calibration is not loaded')
        if self.__dark_signal is None:
            raise ConfigurationError('Dark signal is not loaded')

        data = self.read_raw()
        return Spectrum(
            intensity=data.intensity - np.mean(self.__dark_signal.intensity, axis=0),
            clipped=data.clipped,
            wavelength=self.__wavelengths,
            exposure=self.__config.exposure,
        )

    # --------        config        --------
    @property
    def config(self) -> Config:
        return self.__config

    @property
    def is_configured(self) -> bool:
        """Возвращает `True`, если спектрометр настроен для чтения обработанных данных"""
        return (self.__dark_signal is not None) and (self.__wavelengths is not None)

    def set_config(self,
                   exposure: Optional[int] = None,
                   n_times: Optional[int] = None,
                   dark_signal_path: Optional[str] = None,
                   wavelength_calibration_path: Optional[str] = None,
                   ):
        """Установить настройки спектрометра. Все параметры опциональны, при
        отсутствии параметра соответствующая настройка не изменяется.

        Params:
            exposure: Время экспозиции (в мс). При изменении темновой сигнал будет сброшен.
            n_times: Количество измерений
            dark_signal_path: Путь к файлу темнового сигнала. Если файл темнового сигнала существует и валиден, он будет загружен.
            wavelength_calibration_path: Путь к файлу данных калибровки по длине волны
        """
        if (exposure is not None) and (exposure != self.__config.exposure):
            self.__config.exposure = exposure
            self.__device.setTimer(self.__config.exposure)

            if self.__dark_signal is not None:
                self.__dark_signal = None
                eprint('Different exposure was set, dark signal invalidated')

        if (n_times is not None):
            self.__config.n_times = n_times

        if (dark_signal_path is not None) and (dark_signal_path != self.__dark_signal_path):
            self.__dark_signal_path = dark_signal_path
            self.__load_dark_signal()

        if (wavelength_calibration_path is not None):
            self.__load_wavelength_calibration(wavelength_calibration_path)


def usb_spectrometer(vid: int = 0x0403, pid: int = 0x6014) -> internal.UsbRawSpectrometer:
    """Create usb spectrometer for Spectrometer creation
    Params:
        vid: Usb vendor id
        pid: Usb product id
    Return:
        Device object needed for Spectrometer creation
    """
    return internal.UsbRawSpectrometer(vid, pid)
