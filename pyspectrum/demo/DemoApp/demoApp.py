import time
from threading import Thread

from PyQt5.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
if __name__ == '__main__':
    from pyspectrum_mock import Spectrometer
    import numpy as np
    from os import path




class GThread(Thread):
    def __init__(self, mainwindow):
        self.running = True
        self.mw=mainwindow
        super().__init__()
    def end(self):self.running=False
    def run(self) -> None:
        while self.running:
            self.mw.button.click()
            #self.mw.spectrum_draw()
            time.sleep(0.1)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.spectrometre = Spectrometer()
        self.graph = pg.PlotWidget()

        t = GThread(self)
        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        self.button = QtWidgets.QPushButton()
        #layout.addWidget(self.button)
        container = QWidget()
        #self.button.setAutoRepeatDelay(100)
        #self.button.setCheckable(True)
        self.button.clicked.connect(self.spectrum_draw)
        #self.button.setAutoRepeat(True)
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.show()
        self.setUpdatesEnabled(True);

        t.start()
        #self.closeEvent(t.end)
    def show_spectre(self):
        data = self.spectrometre.read_spectrum(1)
        self.graph.plot().setData(data.wavelength, np.mean(data.samples, axis=0))
        self.maxWave = data.wavelength[np.argmax(np.mean(data.samples, axis=0))]

    def clear(self):
        self.graph.plotItem.clear()
        self.graph.getPlotItem().clear()

    def spectrum_draw(self):
        self.clear()
        self.show_spectre()
        self.update()


app = QtWidgets.QApplication([])
w = MainWindow()
app.exec()
