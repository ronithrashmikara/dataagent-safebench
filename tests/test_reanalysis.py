import json, math, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import reanalysis_v1_0_1 as ra


class WilsonTests(unittest.TestCase):
    def test_known_value(self):
        # 14/150 matches the v1.0 interval stored in outputs/statistics.json.
        lo, hi = ra.wilson(14, 150)
        self.assertAlmostEqual(100 * lo, 5.64118674770873, places=6)
        self.assertAlmostEqual(100 * hi, 15.05639312756139, places=6)

    def test_bounds_are_clamped(self):
        lo, hi = ra.wilson(0, 30)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)
        lo, hi = ra.wilson(21, 21)
        self.assertEqual(hi, 1.0)
        self.assertLess(lo, 1.0)

    def test_contains_point_estimate(self):
        for k, n in [(1, 10), (8, 75), (29, 75), (57, 148)]:
            lo, hi = ra.wilson(k, n)
            self.assertLessEqual(lo, k / n)
            self.assertGreaterEqual(hi, k / n)

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            ra.wilson(1, 0)
        with self.assertRaises(ValueError):
            ra.wilson(5, 4)


class McNemarTests(unittest.TestCase):
    def test_no_discordance(self):
        self.assertEqual(ra.mcnemar_exact(0, 0), 1.0)

    def test_symmetric_and_capped(self):
        self.assertEqual(ra.mcnemar_exact(3, 9), ra.mcnemar_exact(9, 3))
        self.assertEqual(ra.mcnemar_exact(5, 5), 1.0)

    def test_hand_computed(self):
        # b=0, c=5: two-sided p = 2 * 0.5**5
        self.assertAlmostEqual(ra.mcnemar_exact(0, 5), 2 / 32)
        # b=1, c=4: 2 * (1 + 5) / 32
        self.assertAlmostEqual(ra.mcnemar_exact(1, 4), 12 / 32)

    def test_reproduces_v1_statistics(self):
        stats = json.loads((ROOT / 'outputs/statistics.json').read_text(encoding='utf8'))
        for row in stats['mcnemar']:
            p = ra.mcnemar_exact(row['a_success_b_fail'], row['a_fail_b_success'])
            self.assertTrue(math.isclose(p, row['p_exact'], rel_tol=1e-9), row)


class HolmTests(unittest.TestCase):
    def test_holm_order_and_monotonicity(self):
        adj = ra.holm([0.01, 0.04, 0.03])
        self.assertAlmostEqual(adj[0], 0.03)
        self.assertAlmostEqual(adj[2], 0.06)
        self.assertAlmostEqual(adj[1], 0.06)  # max(0.04 * 1, 0.06)

    def test_holm_caps_at_one(self):
        self.assertEqual(ra.holm([0.6, 0.7]), [1.0, 1.0])


if __name__ == '__main__':
    unittest.main()
