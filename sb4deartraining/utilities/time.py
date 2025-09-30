"""Several utility functions for working with time in audio data."""

# external imports
import numpy as np
# internal imports
from ..config import _SR

def convert_samples_to_seconds(num_samples:int, sr:int=_SR) -> float:
    """Convert the number of audio samples to seconds.
    
    Arguments:
    - num_samples: Number of samples
    - sr: Sample rate
    """
    seconds = num_samples / sr
    return seconds

def convert_seconds_to_samples(seconds:float, sr:int=_SR) -> int:
    """Convert time in seconds to number of audio samples.
    
    Arguments:
    - seconds: Time in seconds
    - sr: Sample rate
    """
    num_samples = int(seconds * sr)
    return num_samples

def convert_samples_to_ms(num_samples:int, sr:int=_SR) -> float:
    """Convert the number of audio samples to milliseconds.
    
    Arguments:
    - num_samples: Number of samples
    - sr: Sample rate
    """
    milliseconds = 1000 * convert_samples_to_seconds(num_samples, sr)
    return milliseconds

def convert_ms_to_samples(ms:float, sr:int=_SR) -> int:
    """Convert time in milliseconds to number of audio samples.
    
    Arguments:
    - ms: Time in milliseconds
    - sr: Sample rate
    """
    num_samples = convert_seconds_to_samples(ms / 1000, sr)
    return num_samples

