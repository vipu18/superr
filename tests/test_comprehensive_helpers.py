import unittest
from comprehensive_pressure_rank import clamp, sigmoid, smooth_rate

class PressureHelperTests(unittest.TestCase):
    def test_clamp(self):
        self.assertEqual(clamp(-2),0)
        self.assertEqual(clamp(2),1)

    def test_sigmoid(self):
        self.assertAlmostEqual(sigmoid(0),0.5)

    def test_smooth_rate(self):
        self.assertEqual(smooth_rate(0,10),0)

if __name__ == '__main__':
    unittest.main()
