from PyQt5.QtCore import QEvent, QThread
from pyspectrum_mock import Spectrometer
import numpy as np
import time
from threading import Thread
from PyQt5.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets


class ButtonClicker(Thread):
    def __init__(self, button):
        self.running = True
        self.sleepTime = 0.1
        self.button = button
        super().__init__()

    def end(self): self.running = False
    def run(self) -> None:
        while self.running:
            self.button.click()
            time.sleep(self.sleepTime)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.spectrometre = Spectrometer()

        self.graph = pg.PlotWidget()
        self.graph.getPlotItem().setMouseEnabled(False, False)

        self.button = QtWidgets.QPushButton()
        self.button.clicked.connect(self.spectrum_draw)

        self.t = ButtonClicker(self.button)

        self.label = QtWidgets.QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        layout.addWidget(self.label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.show()
        self.t.start()

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.Close:
            self.t.end()
            return True
        return QWidget.event(self, event)

    def show_spectre(self):
        data = self.spectrometre.read_spectrum(1)
        self.graph.plot().setData(data.wavelength, np.mean(data.samples, axis=0))
        self.maxWave = data.wavelength[np.argmax(np.mean(data.samples, axis=0))]
        self.label.setText("Max-I Wave: " + str(self.maxWave))

    def clear(self):
        self.graph.getPlotItem().clear()

    def spectrum_draw(self):
        self.clear()
        self.show_spectre()


app = QtWidgets.QApplication([])
w = MainWindow()
app.exec_()
