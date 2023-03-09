from abc import abstractmethod, ABC
from datetime import date
import numpy as np
from fpdf import FPDF
from matplotlib import pyplot as plt
from pyspectrum import Spectrum
import csv


class Savior(ABC):
    @abstractmethod
    def save(self):
        pass


class Saver:
    def _save_in_pdf(self):
        PdfSavior(self._filename, self._data, self._spectrum, self._source_model).save()

    def _save_in_csv(self):
        CsvSavior(self._filename, self._data).save()

    _format_dict = {
        "pdf": _save_in_pdf,
        "csv": _save_in_csv
    }

    def __init__(self):
        self._source_model = ""

    def set_source_model(self, name: str):
        self._source_model = name

    def save(self, filname: str, spectum: Spectrum, data: dict[str,any],saveformat: str):
        parsed_filename=filname.split(".")
        self._data = data
        self._spectrum = spectum
        self._filename = parsed_filename[0]
        #выполняет метод из словаря можно заменить if'ами
        self._format_dict[saveformat](self)


class PdfSavior(FPDF, Savior):
    def __init__(self, filename: str, data, spectrum: Spectrum,
                 source_model: str = "unnamed"):
        super(PdfSavior, self).__init__()
        self._source_model = source_model
        self._filename = filename
        self._data = data
        self._spectrum = spectrum

    def header(self) -> None:
        self.set_y(15)
        self.set_x(100)
        self.set_font("helvetica", "B", 18)
        self.cell(w=20, txt=self._source_model, align="C")

    def footer(self) -> None:
        self.set_y(-15)
        current_date = date.today()
        self.cell(w=50, txt=str(current_date))
        self.set_x(-20)

    def save(self):
        self.add_page()
        self.set_font("helvetica", "B", 8)
        plt.plot(self._spectrum.wavelength, np.mean(self._spectrum.samples, axis=0))

        self.image(plt.figure, x=62.5, y=30, w=100, h=75)
        plt.clf()
        self.set_y(120)
        for i in self._data:
            self.cell(w=10, txt=str(i[0]) + " " + str(i[1]), align="Left")
            self.set_y(self.get_y() + 10)
        self.output(self._filename + '.pdf')


class CsvSavior(Savior):
    def __init__(self, filename: str, data):
        self._filename = filename
        self._data = data

    def save(self):
        with open(self._filename + '.csv', 'w', newline='') as csvfile:
            fieldnames = ['name', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in self._data:
                writer.writerow({'name': i, 'value': self._data[i]})
