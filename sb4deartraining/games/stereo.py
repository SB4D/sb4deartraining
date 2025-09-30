"""A collection of ear training exercises focussed on stereo field recognition."""

# external imports
import random
import numpy as np
# internal/relative importsfrom .templates import OptionButtonExercise
from ._templates import OptionButtonExercise
from ..effects.stereo import StereoControl


class GuessWhere(OptionButtonExercise):

    name = "Guess Where!"

    def __init__(self, level=1):
        if not (type(level) == int and level > 0):
            raise ValueError("Positive integer expected for 'level'.")
        num_choices = 2 * level + 1
        super().__init__(num_choices, mode='center')

    def get_options(self):
        def get_label(val):
            if val == 0:
                return "C"
            elif val > 0:
                return f"{100*val:0.0f}% R"
            elif val < 0:
                return f"{-100*val:0.0f}% L"
        M = self.num_choices
        # if M % 2 == 0:
        #     M += 1
        vals = np.linspace(-1, 1, M)
        options = [{'label':get_label(val), "value":val} for val in vals]
        return options

    def get_fx_chain(self):
        solution = self.solution['value']
        fx_chain = StereoControl(pos=solution).make_fx_chain()
        return fx_chain
    

class GuessTheWidth(OptionButtonExercise):

    name = "Guess How Wide!"

    def get_options(self):
        N = self.num_choices
        vals = np.linspace(0, 1, N)
        options = [{'label':f"{100 * val:0.0f}%", "value":val} for val in vals]
        return options

    def get_fx_chain(self):
        solution = self.solution['value']
        fx_chain = StereoControl(width=solution).make_fx_chain()
        return fx_chain
