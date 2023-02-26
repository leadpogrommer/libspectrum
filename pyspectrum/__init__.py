from .errors import LoadError
from .dataclasses import Data, Spectrum
from .spectrometer import Spectrometer, usb_spectrometer




# FactoryConfig file:
# pixel_start, pixel_end, pixel_reverse
#
# set_config(exposure, n_times, profile_path, dark_signal_path)
#
# init(factory_config_path='./fc.cfg')

