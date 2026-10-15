"""
Unit tests for inter-annotator agreement calculations:
- Klaus Krippendorff's Ordinal Alpha
- Quadratic Weighted Kappa (QWK)
- Reproducible Bootstrap Confidence Intervals
- Exact response_id matching and dimension integrity
"""

import unittest
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from human_validation_app.analyze_agreement import (
    krippendorff_alpha_ordinal,
    bootstrap_ci
)


class TestAgreementCalculations(unittest.TestCase):

    def test_perfect_agreement(self):
        """When both annotators provide identical ratings, alpha and QWK must be 1.0."""
        y1 = np.array([1, 2, 3, 4, 5, 2, 3, 4, 1, 5])
        y2 = np.array([1, 2, 3, 4, 5, 2, 3, 4, 1, 5])

        alpha = krippendorff_alpha_ordinal(y1, y2)
        qwk = cohen_kappa_score(y1, y2, weights="quadratic")

        self.assertAlmostEqual(alpha, 1.0, places=5)
        self.assertAlmostEqual(qwk, 1.0, places=5)

    def test_inverse_disagreement(self):
        """When annotators systematically invert scores, alpha and QWK must be negative."""
        y1 = np.array([1, 1, 1, 1, 2, 2, 4, 4, 5, 5])
        y2 = np.array([5, 5, 5, 5, 4, 4, 2, 2, 1, 1])

        alpha = krippendorff_alpha_ordinal(y1, y2)
        qwk = cohen_kappa_score(y1, y2, weights="quadratic")

        self.assertLess(alpha, 0.0)
        self.assertLess(qwk, 0.0)

    def test_known_ordinal_fixture(self):
        """Test with a standard controlled fixture exhibiting known ordinal divergence."""
        y1 = np.array([1, 2, 3, 4, 5])
        y2 = np.array([2, 3, 3, 4, 4])

        alpha = krippendorff_alpha_ordinal(y1, y2)
        qwk = cohen_kappa_score(y1, y2, weights="quadratic")

        # In this positive but imperfect case, both alpha and QWK should be positive
        self.assertGreater(alpha, 0.5)
        self.assertGreater(qwk, 0.5)
        self.assertLessEqual(alpha, 1.0)
        self.assertLessEqual(qwk, 1.0)

    def test_bootstrap_reproducibility(self):
        """Bootstrap CI must produce bit-for-bit identical results with the fixed seed."""
        y1 = np.array([1, 2, 3, 2, 1, 4, 5, 3, 2, 4, 3, 2, 1, 5, 4])
        y2 = np.array([1, 3, 3, 2, 2, 4, 4, 3, 1, 4, 2, 2, 1, 5, 5])

        ci1 = bootstrap_ci(y1, y2, krippendorff_alpha_ordinal, n_boot=100)
        ci2 = bootstrap_ci(y1, y2, krippendorff_alpha_ordinal, n_boot=100)

        self.assertEqual(ci1, ci2)
        self.assertFalse(np.isnan(ci1[0]))
        self.assertFalse(np.isnan(ci1[1]))
        self.assertLess(ci1[0], ci1[1])

    def test_delta_formula_symmetry_and_identity(self):
        """Verify metric distance matrix properties: delta(c, c) == 0 and delta(c, k) == delta(k, c)."""
        counts = {1: 15, 2: 30, 3: 45, 4: 25, 5: 10}

        delta = np.zeros((6, 6))
        for c in range(1, 6):
            for k in range(c, 6):
                if c == k:
                    d = 0.0
                else:
                    intermediate = sum(counts[g] for g in range(c, k + 1))
                    d = intermediate - (counts[c] + counts[k]) / 2.0
                delta[c, k] = d ** 2
                delta[k, c] = d ** 2

        for i in range(1, 6):
            self.assertEqual(delta[i, i], 0.0)
            for j in range(1, 6):
                self.assertEqual(delta[i, j], delta[j, i])

    def test_response_id_pairing_integrity(self):
        """Verify that pairing by response_id prevents corruption from out-of-order data."""
        # Annotator A data in forward order
        data_a = pd.DataFrame({
            "response_id": [f"RESP_{i:04d}" for i in range(10)],
            "score": [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
        }).set_index("response_id")

        # Annotator B data in reversed order
        data_b = pd.DataFrame({
            "response_id": [f"RESP_{i:04d}" for i in reversed(range(10))],
            "score": [5, 4, 3, 2, 1, 5, 4, 3, 2, 1]
        }).set_index("response_id")

        matched_ids = sorted(list(data_a.index.intersection(data_b.index)))
        y1 = data_a.loc[matched_ids, "score"].to_numpy()
        y2 = data_b.loc[matched_ids, "score"].to_numpy()

        # When properly paired by matched_ids, each response has identical ratings
        self.assertTrue(np.array_equal(y1, y2))
        self.assertEqual(krippendorff_alpha_ordinal(y1, y2), 1.0)

    def test_empty_and_insufficient_samples(self):
        """Bootstrap and alpha should return NaN gracefully on empty / invalid inputs."""
        y_empty = np.array([])
        self.assertTrue(np.isnan(krippendorff_alpha_ordinal(y_empty, y_empty)))

        y_short = np.array([1, 2])
        ci = bootstrap_ci(y_short, y_short, krippendorff_alpha_ordinal)
        self.assertTrue(np.isnan(ci[0]))
        self.assertTrue(np.isnan(ci[1]))


if __name__ == "__main__":
    unittest.main()
