#!/usr/bin/env python3
"""
R5 Refusal-Site Mutation Test Suite for ramanujan_cross_org_symbiosis.py (AUDIT-048).
Pure unittest stdlib, zero bare asserts; tests every refusal guard, exact boundary,
and coordinate-free invariance law across Pillars A, B, and C.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ramanujan import sums_mixers as mod  # noqa: E402


class TestPillarARamanujanSubspaces(unittest.TestCase):
    def test_number_theoretic_functions_and_refusals(self) -> None:
        self.assertEqual(mod.mobius(1), 1)
        self.assertEqual(mod.mobius(2), -1)
        self.assertEqual(mod.mobius(6), 1)
        self.assertEqual(mod.mobius(4), 0)
        self.assertEqual(mod.mobius(12), 0)
        self.assertEqual(mod.euler_totient(1), 1)
        self.assertEqual(mod.euler_totient(12), 4)
        self.assertEqual(mod.euler_totient(24), 8)
        self.assertEqual(mod.ramanujan_sum(1, 0), 1)
        self.assertEqual(mod.ramanujan_sum(6, 0), 2)
        self.assertEqual(mod.ramanujan_sum(6, 1), 1)
        self.assertEqual(mod.ramanujan_sum(6, 2), -1)
        self.assertEqual(mod.ramanujan_sum(6, 3), -2)
        self.assertEqual(mod.positive_divisors(1), [1])
        self.assertEqual(mod.positive_divisors(12), [1, 2, 3, 4, 6, 12])

        with self.assertRaisesRegex(TypeError, "non-bool int"):
            mod.mobius(True)
        with self.assertRaisesRegex(ValueError, "n >= 1"):
            mod.mobius(0)
        with self.assertRaisesRegex(TypeError, "non-bool int"):
            mod.euler_totient(False)
        with self.assertRaisesRegex(ValueError, "n >= 1"):
            mod.euler_totient(0)
        with self.assertRaisesRegex(TypeError, "non-bool ints"):
            mod.ramanujan_sum(True, 1)
        with self.assertRaisesRegex(ValueError, "q >= 1"):
            mod.ramanujan_sum(0, 1)
        with self.assertRaisesRegex(TypeError, "non-bool int"):
            mod.positive_divisors(True)
        with self.assertRaisesRegex(ValueError, "n >= 1"):
            mod.positive_divisors(0)

    def test_projector_and_demo_snr_refusals(self) -> None:
        p1 = mod.ramanujan_projector_matrix(4, 1)
        self.assertEqual(len(p1), 4)
        with self.assertRaisesRegex(TypeError, "non-bool ints"):
            mod.ramanujan_projector_matrix(True, 1)
        with self.assertRaisesRegex(ValueError, "positive"):
            mod.ramanujan_projector_matrix(0, 1)
        with self.assertRaisesRegex(ValueError, "positive"):
            mod.ramanujan_projector_matrix(4, 0)
        with self.assertRaisesRegex(ValueError, "does not divide"):
            mod.ramanujan_projector_matrix(6, 4)

        with self.assertRaisesRegex(ValueError, "non-empty"):
            mod.project_ramanujan_subspace([], 1)
        with self.assertRaisesRegex(ValueError, "positive divisor"):
            mod.project_ramanujan_subspace([Fraction(1)] * 6, 4)
        with self.assertRaisesRegex(ValueError, "positive divisor"):
            mod.project_ramanujan_subspace([Fraction(1)] * 6, 0)
        with self.assertRaisesRegex(ValueError, "non-empty"):
            mod.ramanujan_subspace_energies([])

        r1 = mod.demo_collision_snr_ratio_exact(1)
        self.assertTrue(r1["equals_W_squared"])
        with self.assertRaisesRegex(TypeError, "non-bool int"):
            mod.demo_collision_snr_ratio_exact(True)
        with self.assertRaisesRegex(ValueError, "positive"):
            mod.demo_collision_snr_ratio_exact(0)


class TestPillarBRamanujanMixers(unittest.TestCase):
    def test_exact_psd_certifier_cases_and_refusals(self) -> None:
        # PSD with zero eigenvalue
        psd_zero = mod.exact_symmetric_psd_certify([[1, 1], [1, 1]])
        self.assertTrue(psd_zero["is_psd"])
        self.assertEqual(psd_zero["inertia"], [1, 1, 0])
        # Hyperbolic zero-diagonal indefinite [[0, 1], [1, 0]]
        hyp = mod.exact_symmetric_psd_certify([[0, 1], [1, 0]])
        self.assertFalse(hyp["is_psd"])
        self.assertEqual(hyp["witness"], "hyperbolic_offdiag_pivot")
        # Negative diagonal pivot
        neg = mod.exact_symmetric_psd_certify([[-1, 0], [0, 2]])
        self.assertFalse(neg["is_psd"])
        self.assertEqual(neg["witness"], "negative_diagonal_pivot")

        with self.assertRaisesRegex(ValueError, "non-empty"):
            mod.exact_symmetric_psd_certify([])
        with self.assertRaisesRegex(ValueError, "square"):
            mod.exact_symmetric_psd_certify([[1, 2]])
        with self.assertRaisesRegex(ValueError, "symmetric"):
            mod.exact_symmetric_psd_certify([[1, 2], [3, 1]])

    def test_ramanujan_graph_and_givens_refusals(self) -> None:
        k3 = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
        self.assertTrue(mod.certify_ramanujan_graph(k3, 2, bipartite=False)["is_ramanujan"])
        with self.assertRaisesRegex(ValueError, "degree >= 2"):
            mod.certify_ramanujan_graph([[0, 1], [1, 0]], 1)
        with self.assertRaisesRegex(ValueError, "even vertex count"):
            mod.certify_ramanujan_graph(k3, 2, bipartite=True)
        with self.assertRaisesRegex(ValueError, "regularity"):
            mod.certify_ramanujan_graph([[0, 1], [1, 0]], 2)
        with self.assertRaisesRegex(ValueError, "self-loops"):
            mod.certify_ramanujan_graph([[1, 1], [1, 1]], 2)
        with self.assertRaisesRegex(ValueError, "symmetric 0/1"):
            mod.certify_ramanujan_graph([[0, 2, 0], [0, 0, 2], [2, 0, 0]], 2)
        # Gate-2 coordinate-free vertex relabeling invariance on bipartite graphs + R3 non-bipartite refusal
        heawood, _ = mod._make_bipartite_circulant_matchings(7, (0, 1, 3))
        perm_h = [v for i in range(7) for v in (i, 7 + i)]
        heawood_interleaved = [[heawood[perm_h[i]][perm_h[j]] for j in range(14)] for i in range(14)]
        self.assertTrue(mod.certify_ramanujan_graph(heawood_interleaved, 3, bipartite=True)["is_ramanujan"])
        n24_adj, _ = mod._make_bipartite_circulant_matchings(12, (0, 1, 3, 7))
        perm_24 = [v for i in range(12) for v in (i, 12 + i)]
        n24_interleaved = [[n24_adj[perm_24[i]][perm_24[j]] for j in range(24)] for i in range(24)]
        self.assertTrue(mod.certify_ramanujan_graph(n24_interleaved, 4, bipartite=True)["is_ramanujan"])
        # Disconnected 2 x K_{3,3} (exercises multi-component BFS) must be non-Ramanujan
        k33_2 = [[0] * 12 for _ in range(12)]
        for off in (0, 6):
            for i in range(3):
                for j in range(3):
                    k33_2[off + i][off + 3 + j] = 1
                    k33_2[off + 3 + j][off + i] = 1
        self.assertFalse(mod.certify_ramanujan_graph(k33_2, 3, bipartite=True)["is_ramanujan"])
        # Non-bipartite Petersen (even n=10, 3-regular, odd 5-cycle) must raise ValueError when bipartite=True
        pet = [[0] * 10 for _ in range(10)]
        for i in range(5):
            for a, b in ((i, (i + 1) % 5), (i, i + 5), (5 + i, 5 + (i + 2) % 5)):
                pet[a][b] = 1
                pet[b][a] = 1
        with self.assertRaisesRegex(ValueError, "not bipartite"):
            mod.certify_ramanujan_graph(pet, 3, bipartite=True)

        q2 = mod.build_exact_pythagorean_givens_mixer(2, [[(0, 1)]])
        self.assertEqual(len(q2), 2)
        with self.assertRaisesRegex(ValueError, "positive even"):
            mod.build_exact_pythagorean_givens_mixer(0, [[(0, 1)]])
        with self.assertRaisesRegex(ValueError, "positive even"):
            mod.build_exact_pythagorean_givens_mixer(3, [[(0, 1)]])
        with self.assertRaisesRegex(ValueError, "cos_q\\^2 \\+ sin_q\\^2 == 1"):
            mod.build_exact_pythagorean_givens_mixer(2, [[(0, 1)]], Fraction(1, 2), Fraction(1, 2))
        with self.assertRaisesRegex(ValueError, "non-empty"):
            mod.build_exact_pythagorean_givens_mixer(2, [])
        with self.assertRaisesRegex(ValueError, "n/2 disjoint edges"):
            mod.build_exact_pythagorean_givens_mixer(4, [[(0, 1)]])
        with self.assertRaisesRegex(ValueError, "invalid matching edge"):
            mod.build_exact_pythagorean_givens_mixer(4, [[(0, 0), (1, 2)]])
        with self.assertRaisesRegex(ValueError, "invalid matching edge"):
            mod.build_exact_pythagorean_givens_mixer(4, [[(0, 1), (1, 2)]])
        with self.assertRaisesRegex(ValueError, "invalid matching edge"):
            mod.build_exact_pythagorean_givens_mixer(4, [[(0, 1), (2, 4)]])


class TestPillarCNumerologyMirages(unittest.TestCase):
    def test_cf_bracketing_pgl2_and_refutation_refusals(self) -> None:
        self.assertEqual(mod.eval_simple_cf_exact([1, 2]), Fraction(3, 2))
        self.assertEqual(mod.eval_simple_cf_exact([0, 1]), Fraction(1, 1))
        with self.assertRaisesRegex(ValueError, "non-empty"):
            mod.eval_simple_cf_exact([])
        with self.assertRaisesRegex(TypeError, "non-bool ints"):
            mod.eval_simple_cf_exact([True])
        with self.assertRaisesRegex(ValueError, "positive integers"):
            mod.eval_simple_cf_exact([1, 0])

        # Exact interval ordering: A < B, B < A, exact touching point (lo == hi == overlapping), invalid lo > hi
        s_ab = mod.certify_cf_disjointness_exact((Fraction(1), Fraction(2)), (Fraction(3), Fraction(4)))
        self.assertTrue(s_ab["disjoint"])
        self.assertEqual(s_ab["ordering"], "A < B")
        s_ba = mod.certify_cf_disjointness_exact((Fraction(5), Fraction(6)), (Fraction(1), Fraction(2)))
        self.assertTrue(s_ba["disjoint"])
        self.assertEqual(s_ba["ordering"], "B < A")
        s_touch = mod.certify_cf_disjointness_exact((Fraction(1), Fraction(2)), (Fraction(2), Fraction(3)))
        self.assertFalse(s_touch["disjoint"])
        s_touch2 = mod.certify_cf_disjointness_exact((Fraction(2), Fraction(3)), (Fraction(1), Fraction(2)))
        self.assertFalse(s_touch2["disjoint"])
        s_pt = mod.certify_cf_disjointness_exact((Fraction(2), Fraction(2)), (Fraction(3), Fraction(3)))
        self.assertTrue(s_pt["disjoint"])
        with self.assertRaisesRegex(ValueError, "lo <= hi"):
            mod.certify_cf_disjointness_exact((Fraction(3), Fraction(2)), (Fraction(1), Fraction(1)))
        with self.assertRaisesRegex(ValueError, "lo <= hi"):
            mod.certify_cf_disjointness_exact((Fraction(1), Fraction(1)), (Fraction(3), Fraction(2)))

        with self.assertRaisesRegex(ValueError, "M must be invertible"):
            mod.pgl2_quadratic_fixed_point_check(((1, 2), (2, 4)), ((1, 0), (0, 1)))
        with self.assertRaisesRegex(ValueError, "P must be invertible"):
            mod.pgl2_quadratic_fixed_point_check(((1, 1), (1, 0)), ((1, 1), (1, 1)))

        ref_ok = mod.refute_spurious_quadratic_relation_exact(3, 2, (1, 0, -2), mod_prime=2)
        self.assertTrue(ref_ok["refuted_exactly"])
        with self.assertRaisesRegex(TypeError, "non-bool ints"):
            mod.refute_spurious_quadratic_relation_exact(True, 2, (1, 0, -2))
        with self.assertRaisesRegex(ValueError, "q must be positive"):
            mod.refute_spurious_quadratic_relation_exact(3, 0, (1, 0, -2))
        with self.assertRaisesRegex(ValueError, "mod_prime > 1"):
            mod.refute_spurious_quadratic_relation_exact(3, 2, (1, 0, -2), mod_prime=1)

    def test_main_and_all_pillars(self) -> None:
        self.assertEqual(mod.main([]), 0)


if __name__ == "__main__":
    unittest.main()
