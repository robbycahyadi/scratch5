"""Focused protocol tests on fabricated data only; never fit an XGBoost model."""

from fractions import Fraction
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

from run_cghil_experiment import (
    choose_threshold,
    encode_frame,
    load_params,
    method_weights,
    split_indices,
)


class ExperimentProtocolTests(unittest.TestCase):
    def test_method_weights_original_and_synthetic_formulas(self):
        # Three positive originals: E has one row and U has two rows.
        y = np.array([0, 1, 0, 1, 1, 0, 0])
        u_mask = np.array([False, False, False, True, True, False, False])
        s = 1
        expected_original = {
            "M0": [1, 1, 1, 1, 1, 1, 1],
            "M1": [1, 1 + 2 / 3, 1, 1 + 2 / 3, 1 + 2 / 3, 1, 1],
            "M2": [1, 1, 1, 1, 1, 1, 1],
            "M3": [1, 1 + 1 / 3, 1, 1 + 1 / 3, 1 + 1 / 3, 1, 1],
            "M4": [1, 1, 1, 1 + 1 / 2, 1 + 1 / 2, 1, 1],
        }
        for method, originals in expected_original.items():
            with self.subTest(method=method):
                n_syn = {"M0": 0, "M1": 0, "M2": 2 * s,
                         "M3": s, "M4": s}[method]
                weights = np.asarray(method_weights(method, y, u_mask, s))
                self.assertEqual(weights.shape, (len(y) + n_syn,))
                np.testing.assert_allclose(weights[:len(y)], originals)
                np.testing.assert_array_equal(weights[len(y):], np.ones(n_syn))
                np.testing.assert_array_equal(weights[:len(y)][y == 0], 1)
                effective_positive = weights[:len(y)][y == 1].sum() + n_syn
                self.assertAlmostEqual(effective_positive, 3 if method == "M0" else 5)

    def test_weights_use_supplied_s_and_unequal_u_size(self):
        y = np.array([1, 0, 1, 1, 1, 1, 0, 1])
        u_mask = np.array([False, False, True, True, True, False, False, False])
        s = 2
        for method in ("M1", "M2", "M3", "M4"):
            with self.subTest(method=method):
                weights = np.asarray(method_weights(method, y, u_mask, s))
                n_syn = 2 * s if method == "M2" else s if method in ("M3", "M4") else 0
                self.assertEqual(len(weights), len(y) + n_syn)
                self.assertAlmostEqual(weights[:len(y)][y == 1].sum() + n_syn, 10)
                np.testing.assert_array_equal(weights[len(y):], np.ones(n_syn))
                if method == "M4":
                    np.testing.assert_allclose(weights[:len(y)][u_mask], 1 + s / 3)
                    np.testing.assert_array_equal(weights[:len(y)][~u_mask], 1)

    def test_split_exactly_matches_two_stage_sklearn(self):
        y = np.tile([0, 0, 0, 0, 1], 40)
        indices = np.arange(len(y))
        expected_train, holdout = train_test_split(
            indices, test_size=0.30, stratify=y, random_state=42)
        expected_val, expected_test = train_test_split(
            holdout, test_size=0.50, stratify=y[holdout], random_state=42)
        actual = split_indices(y)
        for observed, expected in zip(actual, (expected_train, expected_val, expected_test)):
            np.testing.assert_array_equal(observed, expected)
        self.assertEqual(len(actual), 3)
        train, val, test = map(set, actual)
        self.assertFalse(train & val)
        self.assertFalse(train & test)
        self.assertFalse(val & test)
        self.assertEqual(train | val | test, set(indices))
        self.assertEqual(tuple(map(len, actual)), (140, 30, 30))

    @staticmethod
    def brute_force_threshold(y, probabilities):
        # Independent exact-rational oracle: no floating-point tie comparison.
        candidates = []
        for threshold in np.unique(probabilities):
            predicted = probabilities >= threshold
            tp = int(np.count_nonzero(predicted & (y == 1)))
            fp = int(np.count_nonzero(predicted & (y == 0)))
            fn = int(np.count_nonzero(~predicted & (y == 1)))
            denominator = 2 * tp + fp + fn
            score = Fraction(2 * tp, denominator) if denominator else Fraction(0)
            candidates.append((score, float(threshold)))
        score, threshold = max(candidates)
        return threshold, float(score)

    def test_threshold_matches_unique_candidate_brute_force(self):
        cases = [
            ([1, 0, 0, 1], [.9, .8, .7, .6]),
            ([0, 1, 1, 0, 1], [.2, .2, .7, .7, .9]),
            ([0, 0, 0], [.1, .8, .8]),
            ([1, 1, 1], [.3, .6, .9]),
            ([0, 1, 0, 1], [.5, .5, .5, .5]),
        ]
        rng = np.random.default_rng(42)
        for _ in range(30):
            cases.append((rng.integers(0, 2, 20), rng.integers(0, 11, 20) / 10))
        for labels, probabilities in cases:
            y, p = np.asarray(labels), np.asarray(probabilities)
            with self.subTest(y=y.tolist(), p=p.tolist()):
                threshold, f1 = choose_threshold(y, p)
                expected_threshold, expected_f1 = self.brute_force_threshold(y, p)
                self.assertEqual(threshold, expected_threshold)
                self.assertAlmostEqual(f1, expected_f1, places=14)

    def test_threshold_exact_f1_tie_chooses_largest(self):
        threshold, f1 = choose_threshold(
            np.array([1, 0, 0, 1]), np.array([.9, .8, .7, .6]))
        self.assertEqual(threshold, .9)
        self.assertAlmostEqual(f1, 2 / 3)

    def test_params_are_literal_approved_protocol(self):
        self.assertEqual(load_params(), {
            "objective": "binary:logistic",
            "tree_method": "hist",
            "n_estimators": 300,
            "max_depth": 4,
            "learning_rate": 0.05,
            "min_child_weight": 5,
            "subsample": 1.0,
            "colsample_bytree": 1.0,
            "reg_lambda": 1.0,
            "reg_alpha": 0.0,
            "gamma": 0.0,
            "scale_pos_weight": 1.0,
            "random_state": 42,
            "n_jobs": 4,
            "eval_metric": "logloss",
        })

    def test_encode_preserves_numeric_nan_unknown_and_external_encoder(self):
        categorical = ["category"]
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        encoder.fit(pd.DataFrame({"category": ["known", "__MISSING__", "XNA", "Unknown"]}))
        categories_before = [values.copy() for values in encoder.categories_]
        frame = pd.DataFrame({
            "category": ["novel", "known", "__MISSING__", "XNA", "Unknown"],
            "number": [np.nan, 2.5, 0.0, -1.0, np.nan],
            "unused": [10, 20, 30, 40, 50],
        }, index=[9, 7, 5, 3, 1])
        before = frame.copy(deep=True)
        features = ["number", "category"]
        expected_codes = encoder.transform(frame[categorical]).ravel()
        with patch.object(encoder, "fit", side_effect=AssertionError("encoder must not refit")), \
             patch.object(encoder, "fit_transform", side_effect=AssertionError("encoder must not refit")):
            encoded = encode_frame(frame, features, categorical, encoder)
        self.assertIsInstance(encoded, pd.DataFrame)
        self.assertEqual(list(encoded.columns), features)
        pd.testing.assert_index_equal(encoded.index, frame.index)
        self.assertTrue(all(dtype == np.dtype("float64") for dtype in encoded.dtypes))
        np.testing.assert_array_equal(encoded["category"], expected_codes)
        self.assertEqual(encoded.loc[9, "category"], -1)
        np.testing.assert_allclose(encoded["number"], frame["number"], equal_nan=True)
        pd.testing.assert_frame_equal(frame, before)
        for actual, expected in zip(encoder.categories_, categories_before):
            np.testing.assert_array_equal(actual, expected)


if __name__ == "__main__":
    unittest.main()
