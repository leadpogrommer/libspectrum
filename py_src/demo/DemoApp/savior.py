from datetime import date
import string
import numpy as np
from fpdf import FPDF
from matplotlib import pyplot as plt
from pyspectrum import Spectrum
import csv
class PdfSavior(FPDF):
    def __init__(self):
        super(PdfSavior, self).__init__()
    def footer(self) -> None:
        self.set_y(-15)
        current_date = date.today()
        self.cell(10,15,str(current_date))

    def save_in_pdf(self,filename: string, data, spectrum: Spectrum):
        self.add_page()
        self.set_font("helvetica", "B", 8)
        plt.plot(spectrum.wavelength, np.mean(spectrum.samples, axis=0))
        plt.savefig(filename + '.png')
        self.image(filename + '.png', 5, 5, 100, 75)
        plt.clf()
        x = 100
        y = 150
        self.cell(x, y, str(data))
        self.output(filename + '.pdf')
class CsvSavior():
    def __init__(self):
        pass
    def save_in_csv(self,filename: string, data):
        with open(filename+'.csv', 'w', newline='') as csvfile:
            fieldnames = ['name', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in data:
                writer.writerow({'name': i[0], 'value': i[1]})
