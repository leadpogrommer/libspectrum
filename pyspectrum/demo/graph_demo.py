def graph_demo():
    from pyspectrum import Spectrometer, usb_spectrometer
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib
    from matplotlib.widgets import Button
    from os import path
    from time import time

    d = Spectrometer(usb_spectrometer())

    matplotlib.use("Qt5agg")
    figure, axs = plt.subplots(ncols=2)
    ax = axs[0]

    figure.subplots_adjust(bottom=0.2)

    running = True

    def on_close(_):
        nonlocal running
        running = False

    def read_dark_signal(_):
        ret = d.read_dark_signal(10)

    figure.canvas.mpl_connect('close_event', on_close)

    ax_dark = figure.add_axes([0.5, 0.05, 0.2, 0.075])
    ax_profile = figure.add_axes([0.71, 0.05, 0.2, 0.075])

    b_dark = Button(ax_dark, 'Read dark signal')
    b_dark.on_clicked(read_dark_signal)

    b_profile = Button(ax_profile, 'Load profile data')
    profile_path = path.join(path.dirname(path.realpath(__file__)), 'profile.json')
    b_profile.on_clicked(lambda e: d.set_config(profile_path=profile_path))

    n_times = 1
    d.set_config(n_times=n_times, exposure=100)

    while running:
        read_start = time()
        if d.is_configured:
            data = d.read()
            wl = data.wavelength
        else:
            data = d.read_raw()
            wl = np.array(range(0, data.n_numbers))
        read_time = time() - read_start

        # print(f'Read data took {read_time}, {read_time/n_times} per frame')

        # print(data)

        ax.clear()
        axs[1].clear()
        ax.plot(wl, np.mean(data.intensity, axis=0))
        axs[1].plot(wl, np.max(data.clipped, axis=0))
        plt.pause(0.05)
