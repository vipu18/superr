import unittest

import pandas as pd

from rank_scouting import rr_bonus, shortlist


class ScoutingTests(unittest.TestCase):
    def test_local_evidence_only_and_cap(self):
        frame = pd.DataFrame({'venue_id': ['6', '1241', '999'], 'weight': [1., 1., 1.],
                              'weighted': [1., 2., 100.]})
        self.assertAlmostEqual(rr_bonus(frame), 30 / 102)
        self.assertEqual(rr_bonus(frame.iloc[2:]), 0)
        self.assertEqual(rr_bonus(frame.assign(weighted=-1)), 0)
        self.assertEqual(rr_bonus(frame.assign(weighted=100)), 3)

    def test_availability_and_tier_precedence(self):
        pool = pd.DataFrame({'player_id': range(5), 'released_by': ['MI','DC','GT','KKR','RR'], 'availability':
                             ['release only', 'withdrawn', 'confirmed', 'retired', 'confirmed']})
        scores = pd.DataFrame({'player_id': range(5), 'score': [2., 5., 4., 6., 3.],
                               'evidence_tier': [1, 1, 2, 1, 1], 'pressure_balls': [90] * 5})
        self.assertEqual(shortlist(scores, pool, set()).player_id.tolist(), [0, 2])
