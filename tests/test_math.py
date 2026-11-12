"""Tests that do not require the competition's licensed input CSV files."""
import math
import unittest
from advanced_pressure_rank import clamp, smooth_rate, WICKET_RUN_VALUE, TIME_WEIGHT

class ModelMathTests(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(-10),0)
        self.assertEqual(clamp(12),1)
        self.assertAlmostEqual(clamp(.44),.44)
        self.assertEqual(clamp(-3,-5,5),-3)
    def test_smoothing(self):
        self.assertEqual(smooth_rate(0,100),0)
        self.assertTrue(smooth_rate(6,50) > 0)
        self.assertTrue(smooth_rate(-6,50) < 0)
        self.assertGreater(smooth_rate(100,1000),smooth_rate(10,100))
    def test_weights(self):
        self.assertEqual(WICKET_RUN_VALUE,6.0)
        self.assertGreater(TIME_WEIGHT[2026],TIME_WEIGHT[2025])
        self.assertGreater(TIME_WEIGHT[2025],TIME_WEIGHT[2024])

if __name__=="__main__":unittest.main()
