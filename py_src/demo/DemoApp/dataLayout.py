from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QBoxLayout, QWidget
from dataEstimator import DataEstimator
from pyspectrum_mock import Spectrum
from savior import Savior


class DataLayout(QBoxLayout):
    def __init__(self,parent: QWidget):
        super(QBoxLayout, self).__init__(QBoxLayout.Direction(3))
        self.mainWindow=parent
        self._estimator=DataEstimator()
        self._button=QtWidgets.QPushButton("Save")
        self._button.clicked.connect(self._save)
        self._button.setDisabled(True)
        self.addWidget(self._button)
        self._spectrum=None
        self._calculated_data=None
        self._calculated_data_label=QtWidgets.QLabel()
        self._pdf_savior=Savior()
        self.addWidget(self._calculated_data_label)
    def _save(self):
        dialog=QtWidgets.QInputDialog()
        text,ok=dialog.getText(self.mainWindow,"Save file","Enter a filename:")
        while text == "" and ok:
            text,ok=dialog.getText(self.mainWindow,"Save file","Filename must not be empty")
        if ok:
            self._pdf_savior.save_in_pdf(text, self._calculated_data, self._spectrum)
    def calculateData(self,spectrum:Spectrum):
        self._spectrum=spectrum
        self._calculated_data=self._estimator.calculate(spectrum)
        mystr=""
        for i in self._calculated_data:
            mystr+=(i[0]+": "+str(i[1]+"\n"))
        self._calculated_data_label.setText(mystr)
        self._button.setDisabled(False)


