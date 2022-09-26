import sys
import matplotlib.pyplot as plt
import matplotlib
sys.path.insert(0, './cmake-build-debug')
import pyspectrum


d = pyspectrum.Device()
d.init()

matplotlib.use("Qt5agg")
figure, ax = plt.subplots()
shadow = d.readFrame()


while True:
    data = d.readFrame()
    for i in range(len(data)):
        data[i] = data[i] - shadow[i]
    # print(data)
    ax.clear()
    ax.plot(data)
    plt.pause(0.05)