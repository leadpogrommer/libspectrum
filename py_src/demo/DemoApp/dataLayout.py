from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QBoxLayout, QWidget
from dataEstimator import DataEstimator
from pyspectrum import Spectrum
from savior import PdfSavior, CsvSavior


class DataLayout(QBoxLayout):
    def __init__(self, parent: QWidget):
        super(QBoxLayout, self).__init__(QBoxLayout.Direction(3), parent=parent)
        self.mainWindow = parent
        self._csv_check = QtWidgets.QCheckBox(".csv")
        self._pdf_check = QtWidgets.QCheckBox(".pdf")
        self._estimator = DataEstimator()
        self._save_button = QtWidgets.QPushButton("Save")
        self._save_button.clicked.connect(self._save)
        self._save_button.setDisabled(True)
        self.addWidget(self._pdf_check)
        self.addWidget(self._csv_check)
        self.addWidget(self._save_button)
        self._spectrum = None
        self._calculated_data = [("0", "0")]
        self._calculated_data_label = QtWidgets.QLabel()
        self.addWidget(self._calculated_data_label)
        self._receiver = ""
        self._source_model = "Unnamed source"
        self._pdf_check.clicked.connect(self._enable_button)
        self._csv_check.clicked.connect(self._enable_button)

    def _enable_button(self):
        self._save_button.setDisabled(not self._pdf_check.isChecked() and not self._csv_check.isChecked())

    def set_source_model(self):
        dialog = QtWidgets.QInputDialog()
        name, ok = dialog.getText(self.mainWindow, "Source model", "Enter model:")
        if ok:
            self._source_model = name

    def set_receiver(self):
        dialog = QtWidgets.QInputDialog()
        name, ok = dialog.getText(self.mainWindow, "Receiver", "Enter Receiver:")
        if ok:
            self._receiver = name

    def _save(self):
        if (self._spectrum == None):
            self.mainWindow.error_window(text="No spectrum registered")
            return
        dialog = QtWidgets.QInputDialog()
        self._pdf_check.setDisabled(True)
        self._csv_check.setDisabled(True)
        filename, ok = dialog.getText(self.mainWindow, "Save file", "Enter a filename:")
        while filename == "" and ok:
            filename, ok = dialog.getText(self.mainWindow, "Save file", "Filename must not be empty")
        if ok:
            try:
                if self._pdf_check.isChecked():
                    _pdf_savior = PdfSavior(self._receiver,self._source_model)
                    _pdf_savior.save_in_pdf(filename, self._calculated_data, self._spectrum)
                if self._csv_check.isChecked():
                    _csv_savior = CsvSavior()
                    _csv_savior.save_in_csv(filename, self._calculated_data)
            except Exception:
                self.mainWindow.error_window(text="Error file save")
        self._pdf_check.setDisabled(False)
        self._csv_check.setDisabled(False)

    def calculateData(self, spectrum: Spectrum):
        self._spectrum = spectrum
        self._calculated_data = self._estimator.calculate(spectrum)
        mystr = ""
        for i in self._calculated_data:
            mystr += (i[0] + ": " + str(i[1] + "\n"))
        self._calculated_data_label.setText(mystr)
