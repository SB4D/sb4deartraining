from unittest import TestCase


from sb4deartraining.games.frequency import FrequencyChoiceEvaluator
class TestFequencyChoiceEvaluator(TestCase):

    def test_evaluate(self):
        evaluate = FrequencyChoiceEvaluator(1000,12).evaluate
        self.assertFalse(evaluate(499),"499")
        self.assertTrue(evaluate(500), "500")
        self.assertTrue(evaluate(1000), "1000")
        self.assertTrue(evaluate(2000), "2000")
        self.assertFalse(evaluate(2001), "2001")