"""A collection of ear training exercises focussed on frequency recognition."""

# external imports
import numpy as np
import random
import ipywidgets as widgets
from IPython.display import display
from time import sleep
# internal/relative imports
from ..config import _JUST_BELOW_NYQUIST
from ..playback.samples import SampleSelector
from ..playback.player import SamplePlayer
from ..effects.filters import ParametricEQ
from ..effects.basic import AudioFxChain
from ..utilities.frequencies import add_semi_tones


#TODO: Code needs to be cleaned up.

class RandomFrequencySelector:
    """Implements frequency selection functions"""

    def get_octave_freqs(self, base=1000, f_min=16, f_max=_JUST_BELOW_NYQUIST):
        # start with base freqency
        octaves = [base]
        # add lower octaves
        lower_octave = base / 2
        while f_min <= lower_octave:
            octaves.append(lower_octave)
            lower_octave /= 2
        # add higher octaves
        higher_octave = base * 2
        while higher_octave <= f_max:
            octaves.append(higher_octave)
            higher_octave *= 2
        # returned list sorted in ascending order
        return sorted(octaves)

    def get_third_freqs(self, base=1000, f_min=16, f_max=_JUST_BELOW_NYQUIST):
        # start with octaves of base in the given range
        octaves = self.get_octave_freqs(base, f_min, f_max)
        # add one more octave below (only for computational purposes)
        octaves.append(min(octaves) / 2)
        # add frequencies one third and two thirds above the octaves
        thirds = []
        for octave in octaves:
            thirds.append(octave)
            thirds.append(octave * 2 ** (1 / 3)) # one third up
            thirds.append(octave * 2 ** (2 / 3)) # two thirds up
        thirds = [f for f in thirds if f_min <= f <= f_max]
        return sorted(thirds)
    
    def select_from_list(self, freqs:list[float]):
        freq = random.choice(freqs)
        return freq
    
    def get_random_third(self, base=1000, f_min=16, f_max=_JUST_BELOW_NYQUIST):
        thirds = self.get_third_freqs(base, f_min, f_max)
        freq = self.select_from_list(thirds)
        return freq
    
    def get_random_freq(self, f_min=40, f_max=20000):
        return random.randint(f_min,f_max)
    
    def get_options(self, base=1000, f_range=(40, 20000), options:int=3):
        a, b = f_range
        thirds = self.get_third_freqs(base, a, b)
        options = random.sample(thirds, options)
        correct_option = random.choice(options)
        return sorted(options), correct_option


class FrequencyChoiceEvaluator:

    def __init__(self, solution:float, tolerance):
        self._solution = solution
        self.tolerance = tolerance
    
    @property
    def solution(self):
        return self._solution
    
    @property
    def tol_range(self):
        f_0 = self.solution
        st = self.tolerance
        f_min = add_semi_tones(f_0, -st)
        f_max = add_semi_tones(f_0, st)
        return (f_min, f_max)

    def evaluate(self, choice:float):
        f_min, f_max = self.tol_range
        is_correct = f_min <= choice <= f_max
        return is_correct


#TODO Refactor using the OptionButtonExercise template class
class GuessTheFrequency:

    def __init__(self,freq_range=(40,20000)):
        self.name = "Guess The Frequency!"
        self.sample_selector = SampleSelector()
        self.freq_selector = RandomFrequencySelector()
        self.freq_range = freq_range
        self.options, self.solution = self.get_options()
        sample = self.get_sample()
        fxs = self.build_fx_chain()
        self.player:SamplePlayer = SamplePlayer(sample, fxs)
        self.choice_buttons:list[widgets.Button] = \
            [widgets.Button(description=f"{option:0.0f} Hz") for option in self.options]
        for button in self.choice_buttons:
            button.on_click(self.evaluate_choice)
        self.restart_button = widgets.Button(description="Start over!")
        self.restart_button.on_click(self._restart_button_click)
    @property
    def num_choices(self):
        return len(self.options)
    @property
    def title_widget(self):
        return widgets.HTML(value=f"<h1>{self.name}</h1>")
    
    #TODO decide how to play this
    def get_options(self):
        freqs = [62.5, 125, 250, 500, 1000, 2000, 4000, 8000]
        freqs = self.freq_selector.get_octave_freqs(1000,40,20000)
        # freqs = self.freq_selector.get_third_freqs(1000,40,20000)
        solution = random.choice(freqs)
        return freqs, solution
    # def get_options(self,options:int):
        # return self.freq_selector.get_options(
        #     f_range=self.freq_range,
        #     options=options)
    
    def get_sample(self):
        return self.sample_selector.get_random_sample()
    
    #TODO make Q and gain flexible
    def build_fx_chain(self):
        solution = self.solution
        filt = ParametricEQ(freq=solution, gain=12)
        fx_chain = AudioFxChain([filt])
        return fx_chain

    def evaluate_choice(self, button:widgets.Button):
        idx = self.choice_buttons.index(button)
        if self.options[idx] == self.solution:
            button.button_style = "success"
        else:
            button.button_style = "danger"
        
    def _restart_button_click(self, button):
        # stop plaback
        self.player.stop()
        sleep(0.25)
        # get new sample
        self.player.sample = self.get_sample()
        # get new gain options
        self.options, self.solution = self.get_options()
        self.player.fxs = self.build_fx_chain()
        # reset choice buttons
        self.reset_choice_buttons()
        # restart playback
        self.player.start()
        # reset effects and effects toggle
        self.player.fx_toggle_box.value = False
        self.player.fxs_on = False

    def reset_choice_buttons(self):
        buttons = self.choice_buttons
        options = self.options
        for idx, button in enumerate(buttons):
            # reset color
            button.button_style = ""
            # reset label
            button.description = f"{options[idx]:0.0f} Hz"
    

    def run(self):
        # display title
        display(self.title_widget)
        # start player
        self.player.run()
        # display the options
        button_box = widgets.HBox(self.choice_buttons)
        display(button_box)
        display(self.restart_button)
