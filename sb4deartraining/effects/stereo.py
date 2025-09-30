"""Tools for working with stereo signals."""

# external imports
import numpy as np
# internal imports
from ..constants import PI, SQRT12
from .basic import AudioEffect

# mid-side orthonormal basis
MID_VEC = np.array([[1], [1]]) * SQRT12
SIDE_VEC = np.array([[1], [-1]]) * SQRT12


def mid_side_split(stereoaudio:np.ndarray) -> np.ndarray:
    """Split stereo signal into mid and side channels"""
    left = stereoaudio[0]
    right = stereoaudio[1]
    mid = convert_stereo_to_mono(stereoaudio)
    side = (left - right) * SQRT12
    return mid, side

def convert_stereo_to_mono(stereoaudio:np.ndarray) -> np.ndarray:
    """Converts stereo signal to mono signal of equal intensity."""
    return np.sum(stereoaudio, axis=0) * SQRT12

def adjust_stereo_width(stereoaudio:np.ndarray, width:float|int=1) -> np.ndarray:
    """Adjust the stereo width of a stereo signal."""
    # bypass for width=1
    if width == 1.:
        return stereoaudio
    # get mid and side channels
    mid, side = mid_side_split(stereoaudio)
    # recombine
    processed_audio = mid * MID_VEC + width * side * SIDE_VEC
    return processed_audio


class StereoControl(AudioEffect):

    name = "Stereo Control"

    def __init__(self, pos:float=0, width:float=1):
        try:
            self.pos = np.clip(pos, -1, 1)
            self.width = np.clip(width, 0, 1)
        except:
            raise ValueError("The arguments expect floating point input.")
        self._coefficients = self.get_coefficients()
    
    def get_coefficients(self):
        pos = self.pos
        # compute coefficients
        if pos == 0:        # center panning
            rho = lam = SQRT12
        elif pos == -1:     # hard left panning
            lam, rho = 1, 0
        elif pos == 1:      # hard left panning
            lam, rho = 0, 1
        else:               # intermediate panning
            # compute angle
            alpha = (pos + 1) / 4 * PI
            # infer coefficients
            lam = np.cos(alpha)
            rho = np.sin(alpha)
        return lam, rho
    
    def apply(self, audiodata:np.ndarray) -> np.ndarray:
        """Places a mono audio signal in the stereo field. The 
        position is encoded as a floating point number between
        -1 and 1. 
        
        Arguments:
        - audiodata: Audio signal as NumPy array, 1d (mono) or 2d (stereo)
        """
        # Case 1: Mono Signals
        if audiodata.ndim == 1:
            lam, rho = self._coefficients
            # compute panned signal (using NumPy's broadcasting)
            processed_audio = np.array([[lam],[rho]]) * audiodata
        # Case 2: Stereo Signals
        if audiodata.ndim == 2:
            # adjust stero width 
            audiodata = adjust_stereo_width(audiodata,self.width)
            # avoid re-centering already centered data
            if self.pos == 0. and (audiodata[0] == audiodata[1]).all():
                return audiodata
            # split into mid-side channels
            mid, side = mid_side_split(audiodata)
            # pan the mid channel to self.pos
            panned_mid = self.apply(mid)
            # add side side information
            sides = side * SIDE_VEC
            processed_audio = panned_mid + sides
        return processed_audio