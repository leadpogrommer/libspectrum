from datetime import date
import string

import numpy as np
from fpdf import FPDF
from matplotlib import pyplot as plt
from pyspectrum import Spectrum

class Savior(FPDF):
    def __init__(self):
        super(Savior, self).__init__()
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
        # pdf.set_xy(-10,-15)
        # pdf.cell(0,0,str(current_date))
        # for i in data:
        # pdf.cell(x, y, str(i))
        self.output(filename + '.pdf')
    def save_in_exel(self):
        pass