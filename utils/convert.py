import numpy as np
import json


def convert(graph_file, output_file, start, stop, reverse):
    data = open(graph_file).readlines()
    data = list(map(lambda a: float(a.split('\t')[0]), data))
    leds = np.arange(start, stop)
    if reverse:
        leds = np.flip(leds)
    leds = list(map(lambda a: int(a), leds))
    result = json.dumps({'wavelengths': data, 'leds': leds})
    open(output_file, 'w').write(result)


if __name__ == '__main__':
    convert('noname.txt', '../py_src/demo/profile.json', 2050, 2050 + 1800, True)