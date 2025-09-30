"""Useful classes for working with audio samples and metadata."""

# external imports
import os
import random
import librosa
import numpy as np
import sounddevice as sd
# internal/relative imports
from ..config import _AUDIO_SAMPLE_PATH, _SR
from ..constants import SQRT12


class AudioSignal:
    """Class to hold audio signals, including their sample data, 
    sample rate, and useful operations."""

    def __init__(self, audiodata:np.ndarray, sr:int):
        """Creates an AudioSignal objects from audio data in the 
        form of a 1d or 2d NumPy array and a sample rate. Mono 
        data is modeled by 1d arrays, while multichannel data is
        modeled in 2d arrays of shape (num_channels, num_samples).
        
        CAUTION: Some libraries (including `sounddevice`) require
        the shape (num_samples, num_channels) for multi-channel 
        data. Transposition might be necessary.
        """
        self.data = audiodata
        self.sr = sr
    
    @classmethod
    def load(cls, file:str, mode:str="native"):
        """Create an AudioSignal instance from an audio file. 
        Currently implemented using `librosa`. 
        
        Aurguments:
        - file: audio file path
        - mode: 'mono' produces a mono signal, 'native' uses the 
        native number of channels, 'center' produces a centered
        stereo signal."""
        # verify input
        MODES = ['native', 'mono', 'center']
        if not (type(mode) == str and mode.lower() in MODES):
            raise ValueError("The following options are available " \
            "for 'mode': 'native', 'mono', 'center'")
        # load audio file
        if mode == 'native':
            audio, sr = librosa.load(file, sr=_SR, mono=False)
        elif mode == 'mono':
            audio, sr = librosa.load(file, sr=_SR, mono=True)
        elif mode == 'center':
            audio, sr = librosa.load(file, sr=_SR, mono=True)
            audio = cls.mono_to_center(audio)
        return cls(audio, sr)
    
    @property 
    def num_channels(self):
        audio_dim = self.data.ndim
        # if audio_dim == 1:
        #     ch = 1
        # if audio_dim == 2:
        #     ch = self.data.shape[0]
        ch = 1 if audio_dim == 1 else self.data.shape[0]
        return ch
    
    @property 
    def num_samples(self):
        if self.data.ndim == 1:
            length = len(self.data)
        else:
            length = self.data.shape[1]
        return length
    
    @staticmethod
    def mono_to_center(monoaudio:np.ndarray) -> np.ndarray:
        """Convert mono signal to eqivalent centered stereo signal."""
        if not (type(monoaudio) == np.ndarray and monoaudio.ndim ==1):
            raise ValueError("Input must be 1d NumPy array.")
        # Duplicate mono channel
        stereo = np.stack([monoaudio] * 2, axis=0)
        # Normalize to equal intensity
        stereo *= SQRT12
        return stereo
    
    def preview(self):
        """Playback the loaded sample once."""
        mono = self.num_channels == 1
        audio = self.data if mono else self.data.T
        sd.play(audio, self.sr)
    
    def get_chunk(self, start_idx:int=0, size:int=1024):
        """Extract a chunk of audio data with given size and starting point."""
        # check if sample is large enough
        if self.num_samples < size:
            raise ValueError('Requested size is longer than signal.')
        end_idx = start_idx + size
        if self.num_channels == 1:
            if end_idx <= self.num_samples:
                chunk = self.data[start_idx:end_idx]
            else:
                until_end = self.data[start_idx:]
                back_from_start = self.data[:end_idx - self.num_samples]
                chunk = np.concatenate((until_end, back_from_start), axis=0)
            return chunk
        else:
            if end_idx <= self.num_samples:
                chunk = self.data[:, start_idx:end_idx]
            else:
                until_end = self.data[:, start_idx:]
                back_from_start = self.data[:, :end_idx - self.num_samples]
                chunk = np.concatenate((until_end, back_from_start), axis=1)
            return chunk


class Sample:
    """Class to store audio and metadata of audio samples."""

    def __init__(self, name:str, path:str, mode='native'):
        self.name = name
        self.path = path
        self.audio = AudioSignal.load(self.path, mode=mode)

    def __str__(self):
        return "SAMPLE: " + self.name

    @property
    def num_channels(self):
        return self.audio.num_channels

    @property
    def num_samples(self):
        return self.audio.num_samples
    
    def get_chunk(self, start_idx:int, size:int=1024) -> np.ndarray:
        return self.audio.get_chunk(start_idx,size)

    def preview(self):
        self.audio.preview()


class SampleSelector():
    """Provides methods to load audio samples from a specified path."""

    def __init__(self, path:str=_AUDIO_SAMPLE_PATH):
        self.path = path 
    
    @property
    def samples(self):
        path = self.path
        samples = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        return samples
    
    def get_random_sample(self, mode='native', path_only=False) -> Sample:
        sample_file = random.choice(self.samples)
        sample_path = os.path.join(self.path, sample_file)
        if path_only:
            return sample_path
        else:
            return Sample(sample_file, sample_path, mode=mode)
