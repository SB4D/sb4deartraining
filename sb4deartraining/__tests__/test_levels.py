from unittest import TestCase

import numpy as np

DB_DOUBLE = 20 * np.log10(2)

class LevelsTest(TestCase):

    def test_convert_ratio_to_db(self):
        from sb4deartraining.utilities.levels import convert_ratio_to_db
        scaling = 2
        db = convert_ratio_to_db(scaling)
        self.assertEqual(int(db), 6)
        self.assertAlmostEqual(db, DB_DOUBLE)
    
    def test_convert_db_to_ratio(self):
        from sb4deartraining.utilities.levels import convert_db_to_ratio
        scaling = convert_db_to_ratio(DB_DOUBLE)
        self.assertAlmostEqual(scaling, 2)

    def test_add_db(self):
        from sb4deartraining.utilities.levels import add_db
        signal_in = np.ones(5)
        signal_out = add_db(signal_in, DB_DOUBLE)
        np.testing.assert_almost_equal(signal_out, 2 * signal_in)
        
