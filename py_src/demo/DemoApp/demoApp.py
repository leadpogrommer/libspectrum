import os

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

    def _create_menu_bar(self):
        menuBar = self.menuBar()

        file = QMenu("&File", self)
        file_load = QAction("load data", self)
        file_load.triggered.connect(self.open_file)

        export = QMenu("&Export", self)

        export_pdf = QAction("Save in PDF", self)
        export_pdf.triggered.connect(lambda: self.file_save_layout.save("pdf"))

        export_csv = QAction("Save in CSV", self)
        export_csv.triggered.connect(lambda: self.file_save_layout.save("csv"))

        export.addAction(export_csv)
        export.addAction(export_pdf)

        spectrometer = QMenu("&Spectrometer", self)
        spectrometer_connect = QAction("Connect to a spectrometer", self)
        spectrometer_read_dark_signal=QAction("Read dark signal",self)
        spectrometer_read_dark_signal.triggered.connect(self.read_dark_signal)
        spectrometer.addAction(spectrometer_read_dark_signal)
        spectrometer.addAction(spectrometer_connect)
        spectrometer_connect.triggered.connect(self.connect_spectrometer)

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
        self._starting_inputs()

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.spectrometer_controller = SpectrometerController()
        self.setWindowTitle("Libspectrum")
        self._init_GUI()
        self._create_menu_bar()
        self.show()
        self._init_spectrometer()

    def stop_controller(self):
        if not self.spectrometer_controller.is_ready():
            return
        else:
            self.spectrometer_controller.end()

    def event(self, event: QtCore.QEvent) -> bool:
        if event.type() == QEvent.Close:
            self.stop_controller()
            return True
        return QWidget.event(self, event)

    def read_dark_signal(self):
        if not self.spectrometer_controller.read_dark_signal():
            self.error_window(text="No spectrometer connected")

    def register_spectrum(self):
        if not self.spectrometer_controller.is_ready():
            return
        if self.spectrometer_controller.is_paused():
            self.spectrometer_controller.pause()
            return
        self.spectrometer_controller.pause()
        self.file_save_layout.calculate_data(self.spectrometer_controller.get_spectrum())

    def error_window(self, title: str = "Error", text: str = "unnamed error"):
        mb = QtWidgets.QMessageBox(parent=self)
        mb.setWindowTitle(title)
        mb.setText(text)
        mb.exec_()

    def connect_spectrometer(self):
        try:
            self.spectrometer_controller.set_spectrum_source(
                pyspectrum.Spectrometer(pyspectrum.usb_spectrometer(0x403, 0x6014)))
        except RuntimeError:
            self.error_window(text="Spectrometer not found")
            return False
        # self.stop_controller()
        self.spectrometer_controller.get_spectrum_update_signal().connect(self.update_func)
        self.spectrometer_controller.start()
        return True

    def open_file(self):
        self.stop_controller()
        dialog = QtWidgets.QFileDialog()
        filename = dialog.getOpenFileName(filter="*.pickle")
        if filename[0] != "":
            self.stop_controller()
            self.spectrometer_controller.set_spectrum_source(FileSpectrometer(filename[0]))
            self.spectrometer_controller.get_spectrum_update_signal().connect(self.update_func)
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

