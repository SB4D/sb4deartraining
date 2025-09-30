# external imports
import numpy as np
# internal/relative imports
from ..config import _SR, _JUST_BELOW_NYQUIST, _BLOCKSIZE


class AudioEffect:
    """Base class for audio effects. Dedicated classes for specific
    effects (e.g. filter, EQ, gain, ...) should be defined as sub-
    classes following the steps below:
    
    1) The class attribute `.name` should be overridden with a name
    for the effects type (e.g. "Low Pass Filter").

    2) The effect parameters should be added as instance attributes
    in the constructor method (e.g. self.cutoff, self.slope).
    
    2) The method `.apply()` needs to be overridden with the code 
    that implements the effect. The audio input is expected to be
    a NumPy ndarray and the output needs to be an array of the same
    dimension and shape.
    """
    # Sample rate
    sr:int = _SR
    # Dummy name for effects category (override in subclasses!)
    name:str = "Generic Audio Effect"

    @property
    def params(self) -> dict:
        """Returns the effect instance attributes as a dictionary.
        (Equivalent to `.__dict__`.)"""
        return self.__dict__
    
    def set_params(self, new_params):
        if self.params:
            for key, val in new_params.items():
                if key in self.params:
                    self.params[key] = val
                else:
                    allowed_keys = ", ".join(f'"{key}"' for key in self.params)
                    raise KeyError(f"Invalid key: '{key}' (allowed: {allowed_keys}")
    
    @staticmethod
    def _verify_audiodata(audiodata:np.ndarray):
        """Check whether the array has the correct dimension and shape:
        - 1d arrays represent mono audio.
        - 2d arrays represent audio using the convention
        that the shape is (2, num_samples)
        """
        if not type(audiodata) == np.ndarray:
            raise TypeError("Audio data must be a NumPy array.")
        elif not audiodata.ndim in {1, 2}:
            raise ValueError("Audio data must be 1d or 2d array.")
        elif audiodata.ndim == 2:
            num_channels = audiodata.shape[0]
            if num_channels != 2:
                raise ValueError("Multi-channel support is currently limited to stereo data which is modeled by 2d arrays of shape (2, num_samples)")

    def apply(self, audiodata):
        """Dummy method to process audio. Needs to be overriden in 
        sub-classes. By default, the unaffected is forwarded. """
        return audiodata
    
    def __call__(self, audiodata:np.ndarray):
        """Apply the effect to audio data."""
        return self.apply(audiodata)

    def __str__(self):
        """Print the effect's category name and its parameters."""
        text = self.name.upper()
        if self.params:
            L = max(len(key) for key in self.params)
            for key, val in self.params.items():
                key += ":"
                text += f"\n- {key:{L+1}s} {val}"
        return text
    
    def make_fx_chain(self):
        """Create an AudioFxChain object containint the effect."""
        return AudioFxChain([self])
    
    def add_to_fx_chain(self, fx_chain):
        fx_chain.fxs.append(self)


class AudioFxChain:
    """Container class for chaining multiple audio effects."""

    def __init__(self, fxs:list[AudioEffect]=[]):
        """Creates a container for multiple audio effects."""
        self.fxs = fxs
    
    def __str__(self):
        text = "Audio Effects Chain".upper()
        for fx in self.fxs:
            params = ", ".join(f"{key}: {val}" for key, val in fx.params.items())
            text += f"\n- {fx.name} ({params})"
        return text 
    
    def __call__(self, audiodata:np.ndarray):
        return self.apply_fxs(audiodata)
    
    def add_fx(self,fx:AudioEffect):
        """Adds add a new effect to the end of the chain."""
        self.fxs.append(fx)
    
    def apply_fxs(self, audiodata:np.ndarray):
        """Applies the effects chain to an audio signal."""

        for fx in self.fxs:
            audiodata = fx(audiodata)
        return audiodata
