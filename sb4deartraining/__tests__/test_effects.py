"""Test cases for audio effects."""
# external import
from unittest import TestCase
import numpy as np
# internal imports
from sb4deartraining.effects.basic import AudioEffect
from sb4deartraining.effects.stereo import StereoControl
from sb4deartraining.playback.samples import AudioSignal
from sb4deartraining.effects.stereo import mid_side_split
from sb4deartraining.effects.stereo import adjust_stereo_width

class TestAudioEffect(TestCase):

    def test_params(self):
        class Effect(AudioEffect):

            def __init__(self, test = "test"):
                self.test = test
        effect = Effect()
        self.assertEqual(effect.params, {"test":"test"}, "Failure in params.")

    def test_set_params(self):
        class Effect(AudioEffect):

            def __init__(self, test = "test"):
                self.test = test
        effect = Effect()
        effect.set_params({"test":"change"})
        self.assertEqual(effect.params, {"test":"change"}, "Failure in set_params.")
        keyerror_handled_correctly = False
        try:
            effect.set_params({"tes":"change"})
        except KeyError:
            keyerror_handled_correctly = True
        self.assertTrue(keyerror_handled_correctly, "Invalid params not handled properly.")

    def test_call(self):
        class Effect(AudioEffect):

            def __init__(self, test = "test"):
                self.test = test
        effect = Effect()
        audiodata = np.zeros(10)
        processed_data = effect(audiodata)
        self.assertTrue((audiodata == processed_data).all())


class TestStereoControl(TestCase):

    def setUp(self):
        self.sc = StereoControl()

    # def test_to_mono(self):
    #     # mono test signal
    #     m = np.ones(909)
    #     # equal power centered steror signal
    #     s = np.stack([m] * 2, axis=0) * np.sqrt(0.5)
    #     # downmix to mono
    #     s_to_m = self.sc.to_mono(s)
    #     # check the result
    #     self.assertIsInstance(s_to_m, np.ndarray, "Mono downmix trouble: Output must be NumPy array")
    #     self.assertEqual(s_to_m.ndim, 1, "Mono downmix trouble: Output must be 1d Numpy array")
    #     np.testing.assert_almost_equal(s_to_m, m)
    
    def test_apply(self):
        # initalized center panning effect
        sc = StereoControl(pos=0, width=1)
        # generate one second of mono white noise
        mono = np.random.sample(sc.sr) * 2 - 1
        # form centered stereo signal
        center = AudioSignal.mono_to_center(mono)
        # appply center panning
        center_panned = sc(center)
        np.testing.assert_equal(center_panned, center)
    
def test_mid_side_split():
    """Check the mid-side split function."""
    # define randem test signals
    stereo = np.random.sample([2,909])
    mono = np.random.sample(909)
    zero = np.zeros(909)
    assert stereo.shape == (2,909)
    assert mono.shape == (909,)
    # process stereo test signal
    stereo_split = mid_side_split(stereo)
    assert type(stereo_split) == tuple
    for ch in stereo_split:
        assert type(ch) == np.ndarray
        assert ch.ndim == 1
        assert len(ch) == stereo.shape[1]
    # create stereo signal without side-component
    all_mid = np.stack([mono, mono], axis=0)
    mid, side = mid_side_split(all_mid)
    np.testing.assert_equal(side, zero)
    # create stereo signal without mid-component
    all_side = np.stack([mono, -mono], axis=0)
    mid, side = mid_side_split(all_side)
    np.testing.assert_equal(mid, zero)

def test_adjust_stereo_width():
    """Test stereo width adjustment."""
    # define randem test signals
    stereo = np.random.sample([2,909])
    # process stereo test signal
    stereo_witdh_1 = adjust_stereo_width(stereo, 1)
    np.testing.assert_equal(stereo_witdh_1, stereo)
    stereo_witdh_0 = adjust_stereo_width(stereo, 0)
    mid_0, side_0 = mid_side_split(stereo_witdh_0)
    np.testing.assert_equal(side_0, np.zeros(909))




        
