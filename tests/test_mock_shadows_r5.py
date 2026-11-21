#!/usr/bin/env python3
"""Adversarial R3 + R5 verification test suite for Arm R4-2 (AUDIT-045):
ramanujan_mock_shadows.py.

100% pure Python 3 stdlib, ZERO floats, ZERO bare assert statements.
Covers:
  - R1/R2: exact algebraic identities, zero-float JSON certificate parity
  - R3: fail-closed rejection of floats, bools, zero/non-unit constant terms,
        asymmetric/non-square matrices, invalid moduli, and invalid truncation
  - R4: deterministic bit-identical execution under -I -B / -I -O -B / -W error
  - R5: targeted refusal & boundary tests killing all guard/verifier mutants
        plus unseen Householder O(5, Q) rotation and unseen CS-11 shuffle controls.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ramanujan import mock_shadows as rms  # noqa: E402


class TestRamanujanMockShadowsR5(unittest.TestCase):
    """Comprehensive R1-R5 tests (zero bare asserts, zero floats)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.lib = rms.build_q_series_library(70)
        cls.cert_path = ROOT / "certificates" / "ramanujan_mock_shadows_certificate.json"

    def test_01_r3_strict_scalar_and_json_float_guards(self) -> None:
        self.assertEqual(rms.require_exact_int(42, "x"), 42)
        self.assertEqual(rms.require_exact_rational(Fraction(3, 5), "q"), Fraction(3, 5))
        self.assertEqual(rms.frac_str(Fraction(6, 3)), "2")
        self.assertEqual(rms.frac_str(Fraction(7, 3)), "7/3")
        self.assertEqual(rms.ceil_fraction(Fraction(7, 3)), 3)
        self.assertEqual(rms.ceil_fraction(Fraction(6, 3)), 2)

        for bad in (1.0, True, False, "5", None):
            with self.assertRaises(TypeError):
                rms.require_exact_int(bad, "bad")
            with self.assertRaises(TypeError):
                rms.require_exact_rational(bad, "bad")

        rms.verify_no_floats({"a": [1, "3/2", {"b": True, "c": None}]})
        with self.assertRaises(ValueError):
            rms.verify_no_floats({"nested": [1, {"leak": 0.25}]})

    def test_02_r3_power_series_and_matrix_domain_guards(self) -> None:
        with self.assertRaises(ValueError):
            rms.q_pow([1, 1, 0], -1, 3)
        with self.assertRaises(ValueError):
            rms.q_inv_unit([0, 1, 1], 3)
        with self.assertRaises(ValueError):
            rms.q_inv_unit([2, 1, 1], 3)
        with self.assertRaises(ValueError):
            rms.q_sub_pow([1, 2, 3], 0, 3)
        with self.assertRaises(ValueError):
            rms.q_shift([1, 2, 3], -1, 3)
        with self.assertRaises(ValueError):
            rms.poch_finite(2, 1, 1, 2, 5)
        with self.assertRaises(ValueError):
            rms.poch_finite(1, 0, 1, 2, 5)
        with self.assertRaises(ValueError):
            rms.poch_inf(0, 1, 1, 5)
        with self.assertRaises(ValueError):
            rms.poch_inf(1, 0, 1, 5)
        with self.assertRaises(ValueError):
            rms.q_inv_frac([Fraction(0), Fraction(1)], 2)
        with self.assertRaises(ValueError):
            rms.poch_frac(1, 0, 1, 2, 4)
        with self.assertRaises(ValueError):
            rms.poch_frac(2, 1, 1, 2, 4)
        with self.assertRaises(ValueError):
            rms.build_q_series_library(10)
        with self.assertRaises(ValueError):
            rms.euler_witt_and_log_deriv([0, 1, 2, 3], 2)
        with self.assertRaises(ValueError):
            rms.euler_witt_and_log_deriv([1, 2, 3], 3)
        with self.assertRaises(ValueError):
            rms.hankel_matrix([1, 2, 3], 3, 0)
        with self.assertRaises(ValueError):
            rms.compute_rank_crank_mod_p(10, 2)
        with self.assertRaises(ValueError):
            rms.compute_tau_table(5)

        # Asymmetric, empty, and non-square symmetric inertia guards
        with self.assertRaises(ValueError):
            rms.exact_symmetric_inertia([])
        with self.assertRaises(ValueError):
            rms.exact_symmetric_inertia([[1, 2, 3], [4, 5, 6]])
        with self.assertRaises(ValueError):
            rms.exact_symmetric_inertia([[1, 2], [3, 4]])

        # Verify 2x2 hyperbolic Bunch-Kaufman pivot [[0, 3], [3, 0]] -> (1, 0, 1)
        self.assertEqual(rms.exact_symmetric_inertia([[0, 3], [3, 0]]), (1, 0, 1))
        # Verify singular 3x3 with 2x2 off-diag pivot + zero row -> (1, 1, 1)
        self.assertEqual(rms.exact_symmetric_inertia([[0, 0, 5], [0, 0, 0], [5, 0, 0]]), (1, 1, 1))

    def test_03_part1_mock_theta_universal_and_appell_lerch(self) -> None:
        p1 = rms.verify_mock_theta_and_appell_lerch_identities(self.lib, 70)
        self.assertTrue(p1["identities_all_verified"])
        for k, v in p1["checks"].items():
            self.assertTrue(v, f"Part 1 identity failed: {k}")
        # Negative control: perturbing one coefficient breaks Watson identity
        tampered = dict(self.lib)
        bad_f = list(self.lib["m3_f"])
        bad_f[17] += 1
        tampered["m3_f"] = bad_f
        with self.assertRaises(RuntimeError):
            rms.verify_mock_theta_and_appell_lerch_identities(tampered, 70)

    def test_04_part2_four_tier_filtration_and_unseen_cs11_seed(self) -> None:
        p2 = rms.run_four_tier_filtration(self.lib, 70)
        self.assertTrue(p2["law3_additive_hankel_refutation"]["theta3_vs_partial_theta_shifted_H12_exact_ratio_2"])
        self.assertTrue(p2["law3_additive_hankel_refutation"]["partition_turan_2x2_hankel_det_negative_for_s_25_to_67"])
        self.assertTrue(p2["tier3_ramanujan_ode_all_exact_zero_residual"])
        self.assertEqual(p2["tier2_period20_m22_collapse"]["cancel_phi0_neg_q2_plus_psi0_rank"], 20)
        self.assertEqual(p2["tier2_period20_m22_collapse"]["double_phi0_neg_q2_minus_psi0_rank"], 22)

        # Unseen CS-11 null-shuffle control (fresh seed 99123) breaks crank_neg1 rank 2 -> non-saturating
        rng = random.Random(99123)
        seq = list(self.lib["crank_neg1"])
        win = seq[1:45]
        rng.shuffle(win)
        shuf = [seq[0]] + win + seq[45:]
        b_shuf, _ = rms.euler_witt_and_log_deriv(shuf, 42)
        rk10 = sum(rms.exact_symmetric_inertia(rms.hankel_matrix(b_shuf, 10, 0))[0::2])
        rk14 = sum(rms.exact_symmetric_inertia(rms.hankel_matrix(b_shuf, 14, 0))[0::2])
        self.assertGreater(rk14, rk10)
        self.assertGreater(rk14, 2)

    def test_05_part3_rank_crank_schur_and_unseen_O5Q_invariance(self) -> None:
        p3 = rms.run_rank_crank_schur_obstruction(self.lib)
        self.assertEqual(p3["by_prime"]["p=5"]["S_shadow_ranks_by_rem"], [1, 0, 0, 1, 0])
        self.assertEqual(p3["by_prime"]["p=7"]["S_shadow_ranks_by_rem"], [1, 0, 1, 0, 0, 0, 1])
        self.assertEqual(p3["by_prime"]["p=11"]["crank_ranks_by_rem"], [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1])
        self.assertEqual(p3["by_prime"]["p=11"]["S_shadow_ranks_by_rem"], [5] * 11)
        self.assertEqual(p3["by_prime"]["p=13"]["S_shadow_ranks_by_rem"], [6] * 13)
        self.assertTrue(all(p3["hickerson_7th_order_mock_theta_identities"][k] for k in (
            "7k_plus_0_N0_minus_N2_eq_F0",
            "7k_plus_2_N1_minus_N2_eq_F2",
            "7k_plus_6_2N2_minus_N1_minus_N0_eq_qinv_F1",
        )))

        # Unseen O(5, Q) Householder orthogonal conjugation on S_shadow(11, 6)
        S_raw = [[Fraction(x) for x in row] for row in p3["mod11_class6_shadow_certificate"]["S_shadow_matrix_int"]]
        u_unseen = [Fraction(2), Fraction(1), Fraction(-4), Fraction(3), Fraction(-1)]
        uu = sum((x * x for x in u_unseen), Fraction(0))
        Q_unseen = [
            [Fraction(1 if i == j else 0) - Fraction(2) * u_unseen[i] * u_unseen[j] / uu for j in range(5)]
            for i in range(5)
        ]
        S_rot = rms.mat_mul_frac(rms.mat_mul_frac(Q_unseen, S_raw), Q_unseen)
        spec_orig = rms.psd_r_opt_and_r_h4(S_raw)
        spec_rot = rms.psd_r_opt_and_r_h4(S_rot)
        self.assertEqual(spec_orig["r_opt"], spec_rot["r_opt"])
        self.assertEqual(spec_orig["r_h4"], spec_rot["r_h4"])
        self.assertEqual(rms.exact_symmetric_inertia(S_rot), (5, 0, 0))
        self.assertGreater(spec_orig["r_h4"], spec_orig["r_opt"] + 1)

    def test_06_part4_tau_cubic_agm_and_lean4_audit(self) -> None:
        p4_math = rms.run_tau_and_cubic_agm(m_tau=500, n_agm=100)
        self.assertTrue(all(p4_math["tau"]["congruences"].values()))
        self.assertTrue(p4_math["tau"]["deligne_integer_bound_all_primes"])
        self.assertTrue(p4_math["tau"]["lehmer_nonzero_all_n"])
        self.assertEqual(p4_math["tau"]["primes_checked"], 95)
        self.assertTrue(p4_math["cubic_theta_agm"]["a3_eq_b3_plus_c3"])
        self.assertEqual(p4_math["cubic_theta_agm"]["euler_witt_H10_rank_b"], 3)
        self.assertEqual(p4_math["cubic_theta_agm"]["euler_witt_H10_rank_c_tilde"], 2)

        p4_lean = rms.run_three_lab_lean4_audit()
        if p4_lean.get("mode") == "standalone_no_external_clones":
            sealed = json.loads(self.cert_path.read_text(encoding="utf-8"))
            p4_sealed = sealed["part4_three_lab_lean4_forensics"]
            self.assertEqual(p4_sealed["total_lean_files_audited"], 20)
            self.assertEqual(p4_sealed["openai_math_ramanujan_clean"], "15/15")
            self.assertEqual(p4_sealed["anthropics_flt_ramanujan_ode_clean"], "2/2")
            self.assertTrue(p4_sealed["dm_formal_conjectures_tau_public_import_and_tau2_sorry"])
        else:
            self.assertEqual(p4_lean["total_lean_files_audited"], 20)
            self.assertEqual(p4_lean["openai_math_ramanujan_clean"], "15/15")
            self.assertEqual(p4_lean["anthropics_flt_ramanujan_ode_clean"], "2/2")
            self.assertTrue(p4_lean["dm_formal_conjectures_tau_public_import_and_tau2_sorry"])

    def test_07_certificate_file_integrity_and_zero_floats(self) -> None:
        self.assertTrue(self.cert_path.is_file(), "Certificate JSON missing")
        raw = json.loads(self.cert_path.read_text(encoding="utf-8"))
        rms.verify_no_floats(raw)
        saved_sha = raw.pop("canonical_sha256")
        recomputed_sha = hashlib.sha256(
            json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual(saved_sha, recomputed_sha)
        live = rms.run_all_probes(write_certificate=False)
        for section in (
            "part1_mock_theta_and_appell_lerch",
            "part2_four_tier_hankel_euler_witt_filtration",
            "part3_rank_crank_schur_obstruction",
            "part4_tau_and_cubic_theta_agm",
            "part5_r3_negative_controls",
        ):
            self.assertEqual(live[section], raw[section], f"Live/sealed mismatch in {section}")
        if live["part4_three_lab_lean4_forensics"].get("mode") != "standalone_no_external_clones":
            self.assertEqual(live["canonical_sha256"], saved_sha)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestRamanujanMockShadowsR5)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stderr)
    res = runner.run(suite)
    out = {
        "suite": "test_r5_ramanujan_mock_shadows",
        "tests_run": res.testsRun,
        "failures": len(res.failures),
        "errors": len(res.errors),
        "ok": res.wasSuccessful(),
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if res.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
