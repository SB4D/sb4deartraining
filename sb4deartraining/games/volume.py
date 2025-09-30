"""A collection of ear training exercises focussed on volume and balance."""

# external imports
import numpy as np
import random
import ipywidgets as widgets
from IPython.display import display
from time import sleep
# internal/relative imports
from ..playback.samples import SampleSelector
from ..playback.player import SamplePlayer
from ..effects.volume import Amplifier
from ..effects.basic import AudioFxChain

#TODO Review and clean up the code.


class RandomGainSelector():

    def __init__(self, db_range=(-24,6), step=1):
        self.db_range = db_range
        self.step = step
    
    @property
    def db_vals(self):
        db_min, db_max = self.db_range
        return np.arange(db_min, db_max+1, self.step)
    
    def get_options(self, options:int=3):
        db_vals = [val for val in self.db_vals]
        options = random.sample(db_vals, options)
        correct_option = random.choice(options)
        return sorted(options), correct_option


#TODO Refactor using the OptionButtonExercise template class
class GuessTheGain:

    def __init__(self,db_range=(-12,6), step=1, num_choices=3):
        self.name = "Guess The Gain!"
        # build effect with random parameter selection
        self.gain_selector = RandomGainSelector(db_range, step)
        self.num_choices = num_choices
        self.options, self.solution = self.get_options(num_choices)
        fxs = self.build_fx_chain()
        # get random sample
        self.sample_selector = SampleSelector()
        sample = self.get_sample()
        # initialize player with sample and fx
        self.player:SamplePlayer = SamplePlayer(sample, fxs)
        # add UI elements
        self.choice_buttons:list[widgets.Button] = \
            [widgets.Button(description=f"{option} dB") for option in self.options]
        for button in self.choice_buttons:
            button.on_click(self.evaluate_choice)
        self.restart_button:widgets.Button = \
            widgets.Button(description="Start over!", button_style="warning")
        self.restart_button.on_click(self._restart_button_click)
    
    def evaluate_choice(self, button:widgets.Button):
        idx = self.choice_buttons.index(button)
        if self.options[idx] == self.solution:
            button.button_style = "success"
        else:
            button.button_style = "danger"
        
    def reset_choice_buttons(self):
        buttons = self.choice_buttons
        options = self.options
        for idx, button in enumerate(buttons):
            # reset color
            button.button_style = ""
            # reset label
            button.description = f"{options[idx]} dB"
    
    def _restart_button_click(self, button):
        # stop plaback
        self.player.stop()
        sleep(0.25)
        # get new sample
        self.player.sample = self.get_sample()
        # get new gain options
        self.options, self.solution = self.get_options(self.num_choices)
        self.player.fxs = self.build_fx_chain()
        # reset choice buttons
        self.reset_choice_buttons()
        # restart playback
        self.player.start()
        # reset effects and effects toggle
        self.player.fx_toggle_box.value = False
        self.player.fxs_on = False


    @property
    def title_widget(self):
        return widgets.HTML(value=f"<h1>{self.name}</h1>")
    
    def get_sample(self):
        return self.sample_selector.get_random_sample()
    
    def get_options(self,options:int):
        return self.gain_selector.get_options(options=options)
    
    def build_fx_chain(self):
        gain = self.solution
        amp = Amplifier(gain)
        fx_chain = AudioFxChain([amp])
        return fx_chain

    def run(self):
        # display title
        display(self.title_widget)
        # start player
        self.player.run()
        # display the options
        button_box = widgets.HBox(self.choice_buttons)
        display(button_box)
        display(self.restart_button)
