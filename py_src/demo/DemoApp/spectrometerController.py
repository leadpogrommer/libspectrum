import time
from threading import Thread

from PyQt5.QtCore import QEvent, QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget
from pyspectrum import Spectrum
from pyspectrum import Spectrometer


class SpectrumUpdateSignal(QObject):
    specter_updated = pyqtSignal()


class SpectrometerController(Thread):
    def __init__(self):
        self._running = True
        self._sleepTime = 0.1
        self._spectrum_update_signal = SpectrumUpdateSignal()
        self._isPaused = False
        self._spectrometer = None
        self._spectrum = None
        self._n_times = 1
        super().__init__()

    def set_spectrum_source(self,spectrum_source):
        """

        :param spectrum_source: setting a source for getting spectrum, spectrometer or file spectrometer
        (for reading files)
        :return:
        """
        self._spectrometer=spectrum_source

    def is_ready(self):
        return not (self._spectrometer is None)

    def set_measurement_cnt(self, n_times:int):
        self._n_times=n_times

    def end(self) -> None:
        self._running = False

    def is_paused(self) -> bool:
        return self._isPaused

    def read_dark_signal(self):
        if self._spectrometer is Spectrometer:
            self._spectrometer.read_dark_signal()
            return True
        return False

    def get_spectrum_update_signal(self) -> pyqtSignal | pyqtSignal:
        return self._spectrum_update_signal.specter_updated

    def pause(self) -> None:
        self._isPaused = not self._isPaused

    def get_spectrum(self) -> Spectrum:
        return self._spectrum

    def run(self) -> None:
        while self._running:
            if not self._isPaused:
                self._spectrum_update_signal.specter_updated.emit()
                self._spectrum = self._spectrometer.read_spectrum(self._n_times)
            time.sleep(self._sleepTime)
