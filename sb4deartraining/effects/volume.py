"""Implementations of level based audio effects. 

As all audio effects in this library, the base class `AudioEffect` 
(defined in `basic.py`) is used to define dedicated subclasses for
effects. Please consult the docstring of `AudioEffect` for further
information."""

# external imports
import numpy as np
# internal/relative imports
from ..constants import PI, SQRT12
from .basic import AudioEffect
from ..utilities.levels import convert_db_to_ratio
from ..utilities.levels import convert_ratio_to_db


class Amplifier(AudioEffect):
    """Simple amplifier."""

    name = "Amplifier"

    def __init__(self, gain_db:float=0, clip:bool=True):
        """Create an amplifier effect to change the level. Hard clipping
        is applied by default.
        
        Arguments:
        - gain_db: Level change in decibels
        - clip: Toggle hard clipping (on=True, off=False)
        """
        self.gain_db:float = gain_db
        self.clip:bool = clip
    
    @property
    def gain_ratio(self):
        """Convert dB level change to ratio for rescaling audio data."""
        return convert_db_to_ratio(self.gain_db)
    
    def apply(self, audiodata):
        """Amplify an audio signal."""
        # rescale the audio data
        audiodata_out = audiodata * self.gain_ratio
        # clip the values if needed
        if self.clip:
            audiodata_out = np.clip(audiodata_out, -1, 1)
        return audiodata_out


class Compressor(AudioEffect):
    """Audio Compressor with threshold, ratio, attack, 
    release, and make-up gain parameters."""

    name = "Compressor"

    def __init__(self, 
                 threshold_db=-24.0, 
                 ratio=4.0,
                 attack_ms=10.0, 
                 release_ms=100.0,
                 makeup_db=0.0):
        # compressor coefficients
        self.threshold_db = threshold_db
        self.ratio = ratio
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self.makeup_db = makeup_db
        # needed for computations
        self._threshold_ratio = convert_db_to_ratio(threshold_db)
        self._makeup_ratio = convert_db_to_ratio(makeup_db)
        self._attack_coeff = self._time_to_coeff(attack_ms)
        self._release_coeff = self._time_to_coeff(release_ms)
        # envelope follower state register
        self._env = 0.0

    def _time_to_coeff(self, time_ms):
        """Computes the time coefficients needed for the 
        envelope follower."""
        return np.exp(-1.0 / (0.001 * time_ms * self.sr))

    def apply(self, audio:np.ndarray) -> np.ndarray:
        """Process a block of samples (NumPy array)."""
        # Case 1: Mono Signals
        if audio.ndim == 1:
            processed_audio = self._process_channel(audio)
        # Case 2: Stereo Signals (more channels possible)
        else: 
            N = audio.shape[0] # number of channels
            processed_channels = [self._process_channel(audio[ch, :]) for ch in range(N)]
            processed_audio =  np.stack(processed_channels, axis=0)
        return processed_audio

    def _process_channel(self, x):
        out = np.zeros_like(x)

        for n, sample in enumerate(x):
            rectified = abs(sample)

            # envelope follower
            if rectified > self._env:
                coeff = self._attack_coeff
            else:
                coeff = self._release_coeff
            self._env = coeff * self._env + (1.0 - coeff) * rectified

            # gain computer
            env_db = convert_ratio_to_db(self._env)
            thresh_db = convert_ratio_to_db(self._threshold_ratio)
            if env_db > thresh_db:
                over_db = env_db - thresh_db
                gain_db = -over_db * (1.0 - 1.0 / self.ratio)
            else:
                gain_db = 0.0

            gain = convert_db_to_ratio(gain_db)
            out[n] = sample * gain * self._makeup_ratio
        return out

