from unittest import TestCase

class TestUtilities(TestCase):

    def test_add_semi_tones(self):
        from sb4deartraining.utilities.frequencies import add_semi_tones
        self.assertEqual(add_semi_tones(1000, -12), 500, "Octave down fails")
        self.assertEqual(add_semi_tones(1000, 0), 1000, "Doing nothing fails")
        self.assertEqual(add_semi_tones(1000, 12), 2000, "Octave up fails")
        self.assertAlmostEqual(add_semi_tones(1000, 3.14), 1000 * 2 **(3.14/12), "Crooked steps fail")

