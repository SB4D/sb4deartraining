"""A collection of tone generators (sine, saw, square, noise, etc)"""

# external imports
import numpy as np
# internal imports
from ..config import _SR, _BLOCKSIZE


class SawOscillator:
    """Saw wave oscillator."""

    def __init__(self, sr=_SR, blocksize=_BLOCKSIZE):
        self.sr = sr
        self.blocksize = blocksize
        self.phase = 0.0
    
    def generate(self, freq:float, vol:float=1):
        t = (np.arange(self.blocksize) + self.phase) / self.sr
        signal = 2.0 * (t * freq - np.floor(0.5 + t * freq))  # sawtooth in [-1,1]
        self.phase = (self.phase + self.blocksize) % self.sr
        if 0 <= vol < 1:
            signal *= vol
        return signal

class NoiseGenerator:
    """White Noise Generator"""

    def __init__(self, sr=_SR, blocksize=_BLOCKSIZE):
        self.sr = sr
        self.blocksize = blocksize
  
    def generate(self, freq=1000, vol=1):
        signal = np.random.randn(self.blocksize)
        if 0 <= vol < 1:
            signal *= vol
        return signal
