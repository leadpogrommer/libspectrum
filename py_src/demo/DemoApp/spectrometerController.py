import time
from threading import Thread
from pyspectrum import Spectrum


class SpectrometerController(Thread):
    def __init__(self,spectrometre):
        self._running = True
        self._sleepTime = 0.1
        self._isPaused = False
        self._specreometer=spectrometre
        self._spectrum=None
        super().__init__()
        def default(spectrum: Spectrum):pass
        self._func=default
    def end(self) -> None:
        self._running = False
    def pause(self) -> None:
        self._isPaused = not self._isPaused
    def set_func(self,new_func):
        self._func=new_func
    def run(self) -> None:
        while self._running:
            if not self._isPaused:
                self._spectrum=self._specreometer.read_spectrum(1)
                self._func(self._spectrum)
            time.sleep(self._sleepTime)