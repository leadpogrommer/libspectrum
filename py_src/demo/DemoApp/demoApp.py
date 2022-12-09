import os
import string

import pyspectrum
from PyQt5.QtCore import QEvent
import dataLayout
from pyspectrum_mock import Spectrometer
from PyQt5.QtWidgets import QWidget, QGridLayout
from PyQt5 import QtCore, QtWidgets
from graphLayout import GraphLayout
from spectrometerController import SpectrometerController


class MainWindow(QtWidgets.QMainWindow):
    def update_func(self, spectrum: pyspectrum.Spectrum):
        self.spectrumLayout.update_function(spectrum)
        self.spectrum = spectrum
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # self.Spectrometer = Spectrometer(pyspectrum.usb_spectrometer(0x403, 0x6014))
        # self.Spectrometer.read_dark_signal(10)
        self.spectrumLayout=GraphLayout(self)
        self.file_save_layout = dataLayout.DataLayout(self)
        self.setWindowTitle("Pyspectrum")
        layout = QGridLayout()
        layout.addLayout(self.spectrumLayout,0,0)
        layout.addLayout(self.file_save_layout,0,1)

        self.spectrum = None
        self.spectrometer_controller=None

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.show()

        spectrometer=self.starting_inputs()
        if spectrometer != None:
            self.spectrometer_controller = SpectrometerController(spectrometer)
            self.spectrometer_controller.set_func(self.update_func)
            self.spectrometer_controller.start()

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.Close:
            if self.spectrometer_controller == None:
                return True
            self.spectrometer_controller.end()
            return True
        if event.type() == QEvent.MouseButtonDblClick:
            if self.spectrometer_controller == None:
                return True
            self.file_save_layout.calculateData(self.spectrometer_controller._spectrum)
            self.spectrometer_controller.pause()
            return True
        return QWidget.event(self, event)
    def error_window(self, title: string="Error",text: string="unnamed error"):
        mb = QtWidgets.QMessageBox()
        mb.setWindowTitle(title)
        mb.setText(text)
        mb.exec_()
    def starting_inputs(self) -> Spectrometer:
        dialog = QtWidgets.QInputDialog()
        lastPicked=0
        while True:
            choice, ok = dialog.getItem(self, "Spectrum source option","Choose import option", ["Spectrometer", "File"], lastPicked, False)
            if not ok:
                break
            if choice == "File":
                lastPicked=1
                filename, ok=dialog.getText(self, "Import file", "FilePath: ")
                while filename == "" and ok:
                    filename, ok = dialog.getText(self, "Import file", "Filename must not be empty")
                if not os.path.isfile(filename) and ok:
                    self.error_window(text="File not found")
                    continue
                if ok:
                    return Spectrometer(filename)
            if choice == "Spectrometer" and ok:
                lastPicked = 0
                try:
                    return pyspectrum.Spectrometer(pyspectrum.usb_spectrometer(0x403, 0x6014), pixel_start=2050, pixel_end=2050+1800, pixel_reverse=True)
                except RuntimeError:
                    self.error_window(text="Spectrometer not found")
