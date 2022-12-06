import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
import numpy as np
from PyQt5.QtWidgets import QBoxLayout, QWidget
from pyspectrum import Spectrum


class GraphLayout(QBoxLayout):
    def __init__(self,parent: QWidget):
        super(GraphLayout, self).__init__(QBoxLayout.Direction(2))
        self._spectrum = None
        self._mainWindow=parent
        self._spectrum_update_button = QtWidgets.QPushButton()
        self._spectrum_update_button.clicked.connect(self._spectrum_draw)
        self._graph = pg.PlotWidget()
        self._graph.getPlotItem().setMouseEnabled(False, False)
        self.addWidget(self._graph)
    def update_function(self,spectrum:Spectrum):
        self._spectrum=spectrum
        self._spectrum_update_button.click()

    def _spectrum_draw(self):
        self._graph.getPlotItem().clear()
        self._graph.plot().setData(self._spectrum.wavelength, np.mean(self._spectrum.samples, axis=0))
        self.maxWave = self._spectrum.wavelength[np.argmax(np.mean(self._spectrum.samples, axis=0))]

