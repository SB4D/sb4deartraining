"""Implementations of some audio effects (filter, volume, panning, 
compression, ...)"""

from .filters import LowPassFilter
from .filters import HighPassFilter
from .filters import ParametricEQ

from .stereo import StereoControl

from .volume import Amplifier
from .volume import Compressor