def graph_demo():
    from pyspectrum import Spectrometer, usb_spectrometer
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib
    from matplotlib.widgets import Button
    from os import path
    from time import time

    d = Spectrometer(usb_spectrometer(0x0403, 0x6014), pixel_start=2050, pixel_end=2050+1800, pixel_reverse=True)

    matplotlib.use("Qt5agg")
    figure, axs = plt.subplots(ncols=2)
    ax = axs[0]

    figure.subplots_adjust(bottom=0.2)

    running = True

    def on_close(_):
        nonlocal running
        running = False

    def rea_dark_signal(_):
        ret = d.load_or_read_and_save_dark_signal(10)
        if ret:
            print('Dark signal was read from the device')
        else:
            print('Dark signal was loaded from a file')

    figure.canvas.mpl_connect('close_event', on_close)

    ax_dark = figure.add_axes([0.5, 0.05, 0.2, 0.075])
    ax_profile = figure.add_axes([0.71, 0.05, 0.2, 0.075])

    b_dark = Button(ax_dark, 'Read dark signal')
    b_dark.on_clicked(rea_dark_signal)

    b_profile = Button(ax_profile, 'Load profile data')
    profile_path = path.join(path.dirname(path.realpath(__file__)), 'profile.json')
    b_profile.on_clicked(lambda e: d.load_calibration_data(profile_path))

    n_times = 1

    while running:
        read_start = time()
        data = d.read_spectrum(n_times)
        read_time = time() - read_start

        # print(f'Read data took {read_time}, {read_time/n_times} per frame')

        # print(data)

        ax.clear()
        axs[1].clear()
        ax.plot(data.wavelength, np.mean(data.samples, axis=0))
        axs[1].plot(data.wavelength, np.max(data.clipped, axis=0))
        plt.pause(0.05)
