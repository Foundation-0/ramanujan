#!/usr/bin/env python3
"""Regression & R5 fail-closed test suite closing Foundation-0/ramanujan issues #2, #3, #4, #5.

Zero bare `assert` statements; runs identically across -I -B, -I -O -B, and -I -B -W error.
"""
from __future__ import annotations

from contextlib import redirect_stdout
from fractions import Fraction
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ramanujan import cli, pgl2_mellin  # noqa: E402


class TestCliUnitGuards(unittest.TestCase):
    """Fast deterministic unit tests exercising 100% of fail-closed guards in ramanujan.cli."""

    def test_01_count_floats_exact(self) -> None:
        self.assertEqual(cli._count_floats({"a": [1, (2, 3.5)]}), 1)
        self.assertEqual(cli._count_floats({1.5: "k"}), 1)
        self.assertEqual(cli._count_floats({"a": [1, True, "x", None]}), 0)

    def test_02_unknown_selector_and_non_dict_and_strict_zero_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cli.run_verify("nonexistent_module")

        orig_sums = cli._MODULES["sums_mixers"]
        with mock.patch.dict(cli._MODULES, {"sums_mixers": (orig_sums[0], orig_sums[1], orig_sums[2], lambda: [1, 2])}):
            with self.assertRaises(RuntimeError):
                cli.run_verify("sums_mixers")

        orig_pgl2 = cli._MODULES["pgl2_mellin"]
        with mock.patch.dict(
            cli._MODULES,
            {"pgl2_mellin": (orig_pgl2[0], orig_pgl2[1], orig_pgl2[2], lambda: {"all_passed": True, "leak": 0.25})},
        ):
            with self.assertRaises(RuntimeError):
                cli.run_verify("pgl2_mellin")

    def test_03_fail_closed_all_passed_and_zero_floats_certified(self) -> None:
        for label, bad_payload in (
            ("explicit_false", {"all_passed": False}),
            ("missing_key", {"schema": "no_all_passed"}),
            ("truthy_int_not_bool", {"all_passed": 1}),
            ("zero_floats_false", {"all_passed": True, "zero_floats_certified": False}),
            ("zero_floats_int_not_bool", {"all_passed": True, "zero_floats_certified": 1}),
        ):
            with self.subTest(case=label):
                orig = cli._MODULES["sums_mixers"]
                patched = (orig[0], orig[1], orig[2], lambda p=bad_payload: p)
                with mock.patch.dict(cli._MODULES, {"sums_mixers": patched}):
                    bundle = cli.run_verify("sums_mixers")
                    self.assertFalse(bundle["receipts"]["sums_mixers"]["verified"])
                    self.assertFalse(bundle["all_verified"])
                    self.assertEqual(bundle["modules_verified"], 0)
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = cli.main(["verify", "--module", "sums_mixers", "--json"])
                    self.assertEqual(rc, 1)
                    self.assertFalse(json.loads(buf.getvalue())["all_verified"])

    def test_04_dynamic_oracle_float_accounting_and_cli_entry_paths(self) -> None:
        btz_exact = {
            "all_passed": True,
            "part_c_niemeier_24_and_quantization": {"sampled_benchmark_executed": False},
        }
        btz_sampled = {
            "all_passed": True,
            "part_c_niemeier_24_and_quantization": {"sampled_benchmark_executed": True, "err": 0.125},
        }
        mock_ok = {"all_passed": True, "zero_floats_certified": True}
        pgl2_ok = {"all_passed": True}
        sums_ok = {"all_passed": True, "diag": 1.25}

        def fake_btz(exact_only: bool = False) -> dict:
            return btz_exact if exact_only else btz_sampled

        patched = {
            "btz_graphs": (cli._MODULES["btz_graphs"][0], cli._MODULES["btz_graphs"][1], False, fake_btz),
            "mock_shadows": (cli._MODULES["mock_shadows"][0], cli._MODULES["mock_shadows"][1], True, lambda: mock_ok),
            "pgl2_mellin": (cli._MODULES["pgl2_mellin"][0], cli._MODULES["pgl2_mellin"][1], True, lambda: pgl2_ok),
            "sums_mixers": (cli._MODULES["sums_mixers"][0], cli._MODULES["sums_mixers"][1], False, lambda: sums_ok),
        }
        with mock.patch.dict(cli._MODULES, patched):
            b_full = cli.run_verify("all", exact_only=False)
            self.assertTrue(b_full["all_verified"])
            self.assertEqual(b_full["modules_verified"], 4)
            self.assertEqual(b_full["receipts"]["btz_graphs"]["oracle_class"], "exact+sampled+anchor")
            self.assertFalse(b_full["receipts"]["btz_graphs"]["exact_math_zero_floats"])
            self.assertFalse(b_full["receipts"]["sums_mixers"]["exact_math_zero_floats"])
            self.assertTrue(b_full["receipts"]["pgl2_mellin"]["exact_math_zero_floats"])

            b_ex = cli.run_verify("all", exact_only=True)
            self.assertTrue(b_ex["all_verified"])
            self.assertEqual(b_ex["receipts"]["btz_graphs"]["oracle_class"], "exact+anchor")
            self.assertEqual(b_ex["receipts"]["btz_graphs"]["diagnostic_float_fields"], 0)
            self.assertTrue(b_ex["receipts"]["btz_graphs"]["exact_math_zero_floats"])

            buf_txt = io.StringIO()
            with redirect_stdout(buf_txt):
                rc_txt = cli.main(["verify", "--exact-only"])
            self.assertEqual(rc_txt, 0)
            self.assertIn("[PASS] btz_graphs", buf_txt.getvalue())

            buf_list = io.StringIO()
            with redirect_stdout(buf_list):
                rc_list = cli.main(["list"])
            self.assertEqual(rc_list, 0)
            self.assertIn("btz_graphs", buf_list.getvalue())

            buf_help = io.StringIO()
            with redirect_stdout(buf_help):
                rc_help = cli.main([])
            self.assertEqual(rc_help, 0)


class TestIssues2Through5(unittest.TestCase):
    def test_01_issue2_zero_dependency_cli_and_btz_without_numpy(self) -> None:
        """Issue #2: blocking numpy must not break `ramanujan list` or `ramanujan verify`."""
        script = (
            "import json, sys\n"
            f"sys.path.insert(0, {str(ROOT)!r})\n"
            "sys.modules['numpy'] = None\n"
            "from ramanujan import cli\n"
            "rc_list = cli.main(['list'])\n"
            "b_pgl2 = cli.run_verify('pgl2_mellin')\n"
            "b_btz = cli.run_verify('btz_graphs')\n"
            "print(json.dumps({\n"
            "  'rc_list': rc_list,\n"
            "  'pgl2_ok': b_pgl2['all_verified'],\n"
            "  'btz_ok': b_btz['all_verified'],\n"
            "  'btz_oracle': b_btz['receipts']['btz_graphs']['oracle_class'],\n"
            "  'btz_floats': b_btz['receipts']['btz_graphs']['diagnostic_float_fields'],\n"
            "  'btz_zero_floats': b_btz['receipts']['btz_graphs']['exact_math_zero_floats'],\n"
            "}))\n"
        )
        proc = subprocess.run(
            [sys.executable, "-I", "-O", "-B", "-W", "error", "-c", script],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertEqual(data["rc_list"], 0)
        self.assertTrue(data["pgl2_ok"])
        self.assertTrue(data["btz_ok"])
        self.assertEqual(data["btz_oracle"], "exact+anchor")
        self.assertEqual(data["btz_floats"], 0)
        self.assertTrue(data["btz_zero_floats"])

    def test_02_issue3_pgl2_fail_closed_on_tampered_pillar(self) -> None:
        """Issue #3: pgl2_mellin must fail closed (all_passed=False, FAILED, rc=1) on pillar failure."""
        orig_p3 = pgl2_mellin.audit_ramanujan_master_and_summation()
        tampered_p3 = json.loads(json.dumps(orig_p3))
        tampered_p3["ramanujan_master_theorem"]["mellin_scale_equivariance_exact"] = False
        with mock.patch.object(pgl2_mellin, "audit_ramanujan_master_and_summation", return_value=tampered_p3):
            rep = pgl2_mellin.run_all()
            self.assertFalse(rep["all_passed"])
            self.assertEqual(rep["epistemic_status"], "FAILED")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = pgl2_mellin.main(["--json"])
            self.assertEqual(rc, 1)

    def test_03_issue4_honest_live_float_accounting(self) -> None:
        """Issue #4: live sums_mixers & btz_graphs(--exact-only) reflect real float counts."""
        b_sums = cli.run_verify("sums_mixers")
        r_sums = b_sums["receipts"]["sums_mixers"]
        self.assertTrue(r_sums["verified"])
        self.assertGreater(r_sums["diagnostic_float_fields"], 0)
        self.assertFalse(r_sums["exact_math_zero_floats"])

        b_exact = cli.run_verify("btz_graphs", exact_only=True)
        r_exact = b_exact["receipts"]["btz_graphs"]
        self.assertTrue(r_exact["verified"])
        self.assertEqual(r_exact["oracle_class"], "exact+anchor")
        self.assertEqual(r_exact["diagnostic_float_fields"], 0)
        self.assertTrue(r_exact["exact_math_zero_floats"])

    def test_04_issue5_mellin_scale_equivariance_non_tautological(self) -> None:
        """Issue #5: verify 3-way independent Mellin scale equivariance and must-fail perturbations."""
        for lam in (Fraction(7, 3), Fraction(2, 5), Fraction(5, 1)):
            ok = pgl2_mellin.verify_mellin_scale_equivariance(lam, max_s=5)
            self.assertTrue(ok["all_exact"], f"lam={lam} failed: {ok}")
        self.assertFalse(pgl2_mellin.verify_mellin_scale_equivariance(Fraction(7, 3), scale_exponent_sign=1)["all_exact"])
        self.assertFalse(pgl2_mellin.verify_mellin_scale_equivariance(Fraction(7, 3), scale_exponent_shift=1)["all_exact"])
        with self.assertRaises(ValueError):
            pgl2_mellin.verify_mellin_scale_equivariance(Fraction(7, 3), corrupt_series_c1=Fraction(1, 3))


if __name__ == "__main__":
    unittest.main()
