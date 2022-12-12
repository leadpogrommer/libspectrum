from datetime import date
import string
import numpy as np
from fpdf import FPDF
from matplotlib import pyplot as plt
from pyspectrum import Spectrum
import csv


class PdfSavior(FPDF):
    def __init__(self, receiver: string = "", source_model: string = "unnamed"):
        super(PdfSavior, self).__init__()
        self._receiver = receiver
        self._source_model = source_model

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
        self.cell(w=50, txt=self._receiver, align="LC")

    def save_in_pdf(self, filename: string, data, spectrum: Spectrum):
        self.add_page()
        self.set_font("helvetica", "B", 8)
        plt.plot(spectrum.wavelength, np.mean(spectrum.samples, axis=0))
        plt.savefig(filename + '.png')
        self.image(name=filename + '.png', x=62.5, y=30, w=100, h=75)
        plt.clf()
        self.set_y(120)
        for i in data:
            self.cell(w=10, txt=str(i[0]) + " " + str(i[1]), align="Left")
            self.set_y(self.get_y() + 10)
        self.output(filename + '.pdf')


class CsvSavior():
    def __init__(self):
        pass

    def save_in_csv(self, filename: string, data):
        with open(filename + '.csv', 'w', newline='') as csvfile:
            fieldnames = ['name', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in data:
                writer.writerow({'name': i[0], 'value': i[1]})
