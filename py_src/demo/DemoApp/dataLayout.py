from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QBoxLayout, QWidget
from dataEstimator import DataEstimator
from pyspectrum import Spectrum
from savior import Saver


class DataLayout(QBoxLayout):
    def __init__(self, parent: QWidget):
        super(QBoxLayout, self).__init__(QBoxLayout.Direction(3))
        self.mainWindow = parent
        self._estimator = DataEstimator()
        self._save_button = QtWidgets.QPushButton("Save")
        self._save_button.clicked.connect(self._save)
        self.addWidget(self._save_button)
        self._spectrum = None
        self._calculated_data = [("0", "0")]
        self._calculated_data_label = QtWidgets.QLabel()
        self.addWidget(self._calculated_data_label)
        self._savior = Saver("pdf")

    def set_source_model(self):
        dialog = QtWidgets.QInputDialog()
        name, ok = dialog.getText(self.mainWindow, "Source model", "Enter model:")
        if ok:
            self._savior.set_source_model(name)

    def set_receiver(self):
        dialog = QtWidgets.QInputDialog()
        name, ok = dialog.getText(self.mainWindow, "Receiver", "Enter Receiver:")
        if ok:
            self._savior.set_receiver(name)

    def _save(self):
        if self._spectrum is None:
            self.mainWindow.error_window(text="No spectrum registered")
            return
        dialog = QtWidgets.QInputDialog()
        filename, ok = dialog.getText(self.mainWindow, "Save file", "Enter a filename:")
        while filename == "" and ok:
            filename, ok = dialog.getText(self.mainWindow, "Save file", "Filename must not be empty")
        if ok:
            try:
                self._savior.save(filename, self._spectrum, self._calculated_data)
            except Exception:
                self.mainWindow.error_window(text="Error file save")

    def calculateData(self, spectrum: Spectrum):
        self._spectrum = spectrum
        self._calculated_data = self._estimator.calculate(spectrum)
        mystr = ""
        for i in self._calculated_data:
            mystr += (i[0] + ": " + str(i[1] + "\n"))
        self._calculated_data_label.setText(mystr)
