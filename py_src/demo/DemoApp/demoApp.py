import os
import string

import pyspectrum
from PyQt5.QtCore import QEvent

import dataLayout
from pyspectrum_mock import FileSpectrometer
from PyQt5.QtWidgets import QWidget, QGridLayout, QMenu, QAction
from PyQt5 import QtCore, QtWidgets
from graphLayout import GraphLayout
from spectrometerController import SpectrometerController


class MainWindow(QtWidgets.QMainWindow):
    def update_func(self):
        self.spectrum = self.spectrometer_controller.get_spectrum()
        self.spectrumLayout.update_function(self.spectrum)

    def _createMenuBar(self):
        menuBar = self.menuBar()

        file = QMenu("&File", self)
        file_load = QAction("load data", self)
        file_load.triggered.connect(self.open_file)

        export = QMenu("&Export", self)
        export_pdf = QMenu("&PDF", self)
        export_pdf_receiver=QAction("Set receiver",self)
        export_pdf_receiver.triggered.connect(self.file_save_layout.set_receiver)

        export_pdf_source_model=QAction("Set source model",self)
        export_pdf_source_model.triggered.connect(self.file_save_layout.set_source_model)
        export_pdf.addAction(export_pdf_source_model)
        export_pdf.addAction(export_pdf_receiver)
        export_csv = QMenu("&CSV", self)

        spectrometer = QMenu("&Spectrometer", self)
        spectrometer_connect = QAction("connect", self)
        spectrometer.addAction(spectrometer_connect)
        spectrometer_connect.triggered.connect(self.connect_spectrometer)

        export.addMenu(export_csv)
        export.addMenu(export_pdf)
        file.addAction(file_load)
        menuBar.addMenu(file)
        menuBar.addMenu(spectrometer)
        menuBar.addMenu(export)

    def _init_GUI(self):
        self.spectrumLayout = GraphLayout(self)
        self.file_save_layout = dataLayout.DataLayout(self)
        button = QtWidgets.QPushButton("Register")
        button.clicked.connect(self.register_spectrum)
        layout = QGridLayout()
        layout.addLayout(self.spectrumLayout, 0, 0)
        layout.addLayout(self.file_save_layout, 0, 1)
        layout.addWidget(button, 1, 0)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _init_spectrometer(self):
        self.spectrum = None
        self.spectrometer_controller = None
        self._starting_inputs()

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Pyspectrum")
        self._init_GUI()
        self._createMenuBar()
        self.show()
        self._init_spectrometer()

    def stop_controller(self):
        if self.spectrometer_controller is None:
            return
        else:
            self.spectrometer_controller.end()

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.Close:
            self.stop_controller()
            return True
        return QWidget.event(self, event)

    def register_spectrum(self):
        if self.spectrometer_controller is None:
            return
        if self.spectrometer_controller.is_paused():
            self.spectrometer_controller.pause()
            return
        self.spectrometer_controller.pause()
        self.file_save_layout.calculateData(self.spectrometer_controller.get_spectrum())

    def error_window(self, title: string = "Error", text: string = "unnamed error"):
        mb = QtWidgets.QMessageBox(parent=self)
        mb.setWindowTitle(title)
        mb.setText(text)
        mb.exec_()

    def connect_spectrometer(self):
        try:
            self.spectrometer_controller = SpectrometerController(
                pyspectrum.Spectrometer(pyspectrum.usb_spectrometer(0x403, 0x6014), pixel_start=2050,
                                        pixel_end=2050 + 1800, pixel_reverse=True))
        except RuntimeError:
            self.error_window(text="Spectrometer not found")
            return False
        #self.stop_controller()
        self.spectrometer_controller.get_spectrum_update_signal().specter_updated.connect(self.update_func)
        self.spectrometer_controller.start()
        return True

    def open_file(self):
        self.stop_controller()
        dialog = QtWidgets.QInputDialog()
        filename, ok = dialog.getText(self, "Import file", "FilePath: ")
        while filename == "" and ok:
            filename, ok = dialog.getText(self, "Import file", "Filename must not be empty")
        if not os.path.isfile(filename) and ok:
            self.error_window(text="File not found")
            return False
        if ok:
            self.stop_controller()
            self.spectrometer_controller = SpectrometerController(FileSpectrometer(filename))
            self.spectrometer_controller.get_spectrum_update_signal().specter_updated.connect(self.update_func)
            self.spectrometer_controller.start()
            return True

    def _starting_inputs(self):
        dialog = QtWidgets.QInputDialog()
        lastPicked = 0
        while True:
            choice, ok = dialog.getItem(self, "Spectrum source option", "Choose import option",
                                        ["Spectrometer", "File"], lastPicked, False)
            if not ok:
                break
            if choice == "File":
                lastPicked = 1
                file = self.open_file()
                if (file):
                    return
            if choice == "Spectrometer" and ok:
                lastPicked = 0
                spectrometer = self.connect_spectrometer()
                if (spectrometer):
                    return
# Todo: add profile data, add dark spectrum, add file choose window