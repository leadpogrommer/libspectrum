from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QBoxLayout, QWidget
from dataEstimator import DataEstimator
from pyspectrum import Spectrum
from savior import Saver


class DataLayout(QBoxLayout):
    def __init__(self, parent: QWidget):
        super(QBoxLayout, self).__init__(QBoxLayout.Direction(3))
        self.mainWindow = parent
        self._spectrum = None
        self._calculated_data = {}
        self._calculated_data_label = QtWidgets.QLabel()
        self.addWidget(self._calculated_data_label)
        self._savior = Saver()

    def set_source_model(self):
        dialog = QtWidgets.QInputDialog()
        name, ok = dialog.getText(self.mainWindow, "Source model", "Enter model:")
        if ok:
            self._calculated_data.update({"Source": name})

    def save(self, savetype: str):
        if self._spectrum is None:
            self.mainWindow.error_window(text="No spectrum registered")
            return
        dialog = QtWidgets.QFileDialog()
        filename = dialog.getSaveFileName(filter=("*." + savetype))
        if filename[0] != "":
            self._savior.save(filename[0], self._spectrum, self._calculated_data, savetype)

    def calculate_data(self, spectrum: Spectrum):
        self._spectrum = spectrum
        self._calculated_data = DataEstimator.calculate(spectrum)
        mystr = ""
        for i in self._calculated_data:
            mystr += i + ": " + str(self._calculated_data[i]) + "\n"
        self._calculated_data_label.setText(mystr)
