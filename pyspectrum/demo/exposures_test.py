def exposures_test():
    from pyspectrum import Spectrometer, usb_spectrometer
    from time import time

    exposures = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 250, 500]
    d = Spectrometer(usb_spectrometer(0x0403, 0x6014))

    for exposure in exposures:
        n = int(min(500, 20 / (exposure / 1000)))
        d.set_timer(exposure)

        print(f'{exposure=} {n=} ...')
        t_start= time()
        d.read_spectrum(n)
        t = time() - t_start

        print(f'{t/n*1000} real exposure, {t} s total\n')