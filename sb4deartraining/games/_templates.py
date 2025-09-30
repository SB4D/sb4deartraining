"""Templates classes for games."""

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
from ..effects.basic import AudioEffect
from ..effects.basic import AudioFxChain


#TODO Include instructions in doc string.
class OptionButtonExercise():
    """Template class for exercises offering a finite number of
    choices one of which is the solution. Currently built for 
    use in Jupyter Notebooks."""

    name = "Dummy Exercise"
    
    def __init__(self, num_choices:int=3, mode='native'):
        self.num_choices = num_choices
        self.mode=mode
        # build effect with random parameter selection
        self.options:list = self.get_options()
        self.solution = self.get_solution()
        # get random sample
        self.sample_selector:SampleSelector = SampleSelector()
        sample = self.get_sample()
        fxs = self.get_fx_chain()
        # initialize player with sample and fx
        self.player:SamplePlayer = SamplePlayer(sample, fxs)
        # add UI elements
        self.choice_buttons:list[widgets.Button] = \
            [widgets.Button(description=option['label']) for option in self.options]
        for button in self.choice_buttons:
            button.on_click(self.evaluate_choice)
        self.restart_button:widgets.Button = \
            widgets.Button(description="Start over!", button_style="warning")
        self.restart_button.on_click(self._restart_button_click)
    
    def get_options(self):
        dummy_options = []
        for i in range(self.num_choices):
            button_label = f"Option {i + 1}"
            val = random.randint(100, 500)
            option = {
                "label":button_label,
                "value":val
            }
            dummy_options.append(option)
        return dummy_options
    
    def get_solution(self):
        solution = random.choice(self.options)
        return solution

    def get_sample(self):
        return self.sample_selector.get_random_sample(mode=self.mode)
    
    def get_fx_chain(self):
        param = self.solution
        fx = AudioEffect()
        fx_chain = AudioFxChain([fx])
        return fx_chain

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
            button.description = options[idx]['label']
    
    def _restart_button_click(self, button):
        # stop plaback
        self.player.stop()
        sleep(0.25)
        # get new sample
        self.player.sample = self.get_sample()
        # get new gain options
        self.options = self.get_options()
        self.solution = self.get_solution()
        self.player.fxs = self.get_fx_chain()
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

    def run(self):
        # display title
        display(self.title_widget)
        # start player
        self.player.run()
        # display the options
        button_box = widgets.HBox(self.choice_buttons)
        display(button_box)
        display(self.restart_button)
