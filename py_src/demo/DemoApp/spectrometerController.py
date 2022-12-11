import time
from threading import Thread

from PyQt5.QtCore import QEvent, QObject, pyqtSignal
from pyspectrum import Spectrum
from pyspectrum import Spectrometer


class SpecterUpdateSignal(QObject):
    specter_updated = pyqtSignal()


class SpectrometerController(Thread):
    def __init__(self, spectrometer):
        self._running = True
        self._sleepTime = 0.1
        self._spectrum_update_signal = SpecterUpdateSignal()
        self._isPaused = False
        self._spectrometer = spectrometer
        self._spectrum = None
        self._n_times = 1
        super().__init__()

    def end(self) -> None:
        self._running = False

    def is_paused(self)->bool:
        return self._isPaused

    def get_spectrum_update_signal(self) -> QObject:
        return self._spectrum_update_signal

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
