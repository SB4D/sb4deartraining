"""Implementations of various IIR audio filter types using SciPy. 

As all audio effects in this library, the base class `AudioEffect` 
(defined in `basic.py`) is used to define dedicated subclasses for
effects. Please consult the docstring of `AudioEffect` for further
information."""

# external imports
import numpy as np
from scipy.signal import lfilter, butter
from scipy.signal import sosfilt, sosfilt_zi, tf2sos
# internal/relative imports
from ..config import _SR, _JUST_BELOW_NYQUIST, _BLOCKSIZE
from .basic import AudioEffect


class Filter(AudioEffect):
    """Base Class for audio filters suitable for use in callbacks of
    audio streams. The implementation uses second-order sections (SOS)
    and a filter state memory as included in SciPy. Dedicated filter 
    types (eg. low pass, peak) can be defined as sub-classes as follows:
    
    1) Override the class attribute `.name` (e.g. "Low Pass Filter").

    2) Override the constructor. Define instance attributes for effect 
    parameters (e.g. cutoff, slope).

    2.2) Define two more instance attributes `self.sos` and `self.zi` 
    for the second-order sections and the filter state. The values must 
    with `scipy.signal.sosfilt`. (Please consult the SciPy documentation 
    for more details.)
    """

    name = "Generic Audio Filter"

    def __init__(self):
        """Dummy constructor. Useless as is. Needs to be overridden in subclasses"""
        self.sos:np.ndarray = None  # filter coefficients
        self.zi:np.ndarray = None   # filter state
    
    def _adjust_zi_to_audiochannels(self, zi:np.ndarray, audiodata:np.ndarray):
        """Adjust the a filter state array to an audio data array in case of a 
        dimension mismatch."""
        # check dimensions
        audio_dim = audiodata.ndim 
        zi_fits_audio = (zi.ndim == audio_dim + 1)
        # reset filter state (zi) and adjust to audiodata
        if not zi_fits_audio:
            # recompute initial state for mono signal
            zi_0 = sosfilt_zi(self.sos)
            # mono case
            if audio_dim == 1:
                zi = zi_0
            # multi-channel case
            elif audio_dim == 2:
                num_channels = audiodata.shape[0]
                zi = np.repeat(zi_0[:, np.newaxis], num_channels, axis=1)
            else:
                raise ValueError('Audio must 1d (mono) or 2d array (multi-channel) with axes (ch, samples).')
        return zi

    def apply(self, audiodata_in:np.ndarray) -> np.ndarray:
        """Process audio data and update the filter state to handle
        block transitions in audio streams."""
        # Get current filter state
        zi_in = self.zi
        # Adjust filter state in case of channel mismatch
        zi_in = self._adjust_zi_to_audiochannels(zi_in, audiodata_in)
        # Apply filter to audio data 
        # NOTE: The audio data is a 1d (mono) or 2d (multi-channel) array:
        # - In the 1d case, the shape is (n_samples)
        # - In the 2d case, the shape is (n_channels, n_samples)
        # In both cases, the "sample axis" comes last, hence axis=-1 below.
        audiodata_out, zi_out = sosfilt(self.sos, audiodata_in, zi=zi_in, axis=-1)
        self.zi = zi_out
        return audiodata_out


class LowPassFilter(Filter):
    """A stable IIR low pass filter using second-order sections (SOS)."""

    name = "Low Pass Filter (Butterworth, SOS)"

    def __init__(self, cutoff:float=_JUST_BELOW_NYQUIST, order:int=5):
        self.cutoff = cutoff
        self.order = order
        self.sos, self.zi = self.get_coefficients()
    
    def get_coefficients(self) -> tuple[np.ndarray]:
        sos = butter(
            btype='low',    # filter type 
            N=self.order,   # filter order
            Wn=self.cutoff, # cutoff frequency
            fs=self.sr,     # sample rate
            output='sos'    # needed for real-time processing
        )
        zi = sosfilt_zi(sos)
        return sos, zi


class HighPassFilter(Filter):
    """A stable IIR high pass filter using second-order sections (SOS)."""

    name = "High Pass Filter (Butterworth, SOS)"

    def __init__(self, cutoff:float=16, order:int=5):
        self.cutoff = cutoff
        self.order = order
        self.sos, self.zi = self.get_coefficients()
    
    def get_coefficients(self) -> tuple[np.ndarray]:
        sos = butter(
            btype='high',   # filter type 
            N=self.order,   # filter order
            Wn=self.cutoff, # cutoff frequency
            fs=self.sr,     # sample rate
            output='sos'    # needed for real-time processing
        )
        zi = sosfilt_zi(sos)
        return sos, zi


class ParametricEQ(Filter):
    """Parametric equalizer (biquad peaking filter)."""

    name = "Parametric EQ / Peaking Filter (RBJ, BiQuad, SOS)"

    def __init__(self, freq=1000, q=1, gain=0):
        self.freq = freq
        self.q = q
        self.gain = gain
        self.sos, self.zi = self.get_coefficients()
    
    def get_coefficients(self):
        A = 10 ** (self.gain / 40)
        w0 = 2 * np.pi * self.freq / self.sr
        alpha = np.sin(w0) / (2 * self.q)
        b0 = 1 + alpha * A
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A
        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1 / a0, a2 / a0])
        # Convert to SOS for numerical stability
        sos = tf2sos(b, a)
        zi = sosfilt_zi(sos)
        return sos, zi
