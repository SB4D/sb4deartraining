"""Audio playback functionality."""

# external imports
import sounddevice as sd
from threading import Thread
from time import sleep
import ipywidgets as widgets
from IPython.display import display
# internal/relative imports
from .samples import Sample
from ..effects.basic import AudioFxChain


class SamplePlayer:
    """Simple audio player with built-in effects loop built
    for use in Jupyter Notebooks. Includes simple transport 
    controls and effects toggle. Playback is looped."""

    def __init__(self, 
                 sample:Sample, 
                 fx_chain:AudioFxChain=None, 
                 play_on_start=False,
                 fxs_on=False, 
                 buffer=1024):
        """Loads a sample and effects chain into an audio 
        player for use in Jupyter Notebooks. The player 
        uses the `sounddevice` module for streaming audio.
        
        Arguments:
        - sample: an audio sample (see Sample class)
        - fx_chain: an effects chain (see AudioFxChain class)
        - play_on_start: playback state on player start
        - play_on_start: effects stats on player start
        - buffer: buffer length for audio stream callback
        """
        # load sample
        self.sample = sample
        # needed for playback functionality
        self.idx = 0
        self.stop_flag = not play_on_start
        self.buffer = buffer
        self._audio_thread:Thread = None
        # transport control
        self.start_button:widgets.Button = \
            widgets.Button(description="▶ Play / Loop", button_style="success")
        self.stop_button:widgets.Button = \
            widgets.Button(description="⏹ Stop", button_style="danger")
        self.start_button.on_click(self._start_button_click)
        self.stop_button.on_click(self._stop_button_click)
        # load audio effect
        self.fxs:AudioFxChain = fx_chain
        self.fxs_on = fxs_on
        # effects toggle
        self.fx_toggle_box:widgets.ToggleButton = \
            widgets.ToggleButton(value=self.fxs_on, description="FXs on/off", button_style="info")
        self.fx_toggle_box.observe(self._fx_toggle_box_click)
    
    # --- Audio Playback ---
    def _new_audio_thread(self):
        self._audio_thread = Thread(target=self._play_audio, daemon=True)

    def _play_audio(self):
        with sd.OutputStream(
            samplerate=self.sample.audio.sr, 
            channels=self.sample.audio.num_channels, 
            blocksize=1024, 
            callback=self._callback):
            while not self.stop_flag:
                sd.sleep(100)  # keep stream alive

    def _callback(self, outdata, frames, time, status):
        # check status
        if status:
            print(status)
        # check stop_flag
        stop_flag = self.stop_flag
        if stop_flag:
            outdata.fill(0)
            raise sd.CallbackStop()
        # get current signal chunk
        start_idx = self.idx
        audio_chunk = self.sample.get_chunk(start_idx, frames)
        # update index attribute
        end_idx = start_idx + frames
        num_samples = self.sample.num_samples
        if end_idx <= num_samples:
            self.idx = end_idx
        else:
            self.idx = end_idx - num_samples
        # apply effects to current signal chunk
        if self.fxs and self.fxs_on:
            # print(f"DEBUGGING: outdata.shape={outdata.shape}")
            # print(f"DEBUGGING: audio_chunk.shape={audio_chunk.shape}")
            audio_chunk = self.fxs(audio_chunk)
        # update outdata variable for playback
        if audio_chunk.ndim == 1:
            outdata[:] = audio_chunk.reshape(outdata.shape)
        else:
            outdata[:] = audio_chunk.T
    
    # --- User Interface ---
    def _build_ui(self):
        elements = [
            self.start_button,
            self.stop_button,
            self.fx_toggle_box,
        ]
        box = widgets.HBox(elements)
        display(box)
    
    def start(self):
        if not self.stop_flag:
            self.stop()
            sleep(0.125)
        self.idx = 0
        self.stop_flag = False
        self._new_audio_thread()
        self._audio_thread.start()
    
    def stop(self):
        self.stop_flag = True

    def _start_button_click(self,but):
        self.start()
    
    def _stop_button_click(self, but):
        self.stop()

    def toggle_fx(self):
        self.fxs_on = not self.fxs_on

    def _fx_toggle_box_click(self, box):
        self.toggle_fx()
    
    # --- Starting the Player --- 
    def run(self):
        self._build_ui()
        if not self.stop_flag:
            self._new_audio_thread()
            self._audio_thread.start()
        
