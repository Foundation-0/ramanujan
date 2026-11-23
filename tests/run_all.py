#!/usr/bin/env python3
"""Master R4-clean test runner for Foundation-0/ramanujan.

Executes:
  1. All four verified modules via `ramanujan.cli.run_verify("all")`
  2. Clean-room R5 unittest suite for `ramanujan.mock_shadows` (AUDIT-045)
  3. Clean-room R5 test suite for `ramanujan.pgl2_mellin` (AUDIT-046)
  4. Clean-room R5 unittest suite for `ramanujan.sums_mixers` (AUDIT-048R)
  5. Clean-room R5 regression suite for issues #2-#5 (`test_cli_and_issues_2_5_r5`)
  6. CLI smoke checks (`list`, `verify --module pgl2_mellin --json`)

Zero required third-party dependencies (optional `numpy` enables `btz_graphs` Part C2);
zero bare `assert`s; bit-identical across all 4 isolated R4 modes
(`-I -B`, `-I -O -B`, `-I -B -W error`, `-I -O -B -W error`).
"""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
for p in (str(ROOT), str(TESTS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from ramanujan import cli  # noqa: E402
import test_cli_and_issues_2_5_r5  # noqa: E402
import test_mock_shadows_r5  # noqa: E402
import test_pgl2_mellin_r5  # noqa: E402
import test_sums_mixers_r5  # noqa: E402


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"RAMANUJAN_TEST_RUNNER_FAILED: {msg}")


def _run_unittest_module(mod: object, label: str) -> int:
    suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
    sink = io.StringIO()
    result = unittest.TextTestRunner(stream=sink, verbosity=0).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError(f"{label} unittest failed:\n{sink.getvalue()}")
    return result.testsRun


def main() -> int:
    # 1. All 4 verified modules
    bundle = cli.run_verify("all")
    require(bundle["all_verified"] is True, "Not all modules verified")
    require(bundle["modules_verified"] == 4, f"Expected 4 modules, got {bundle['modules_verified']}")

    # 2. R5 test suites
    n_mock = _run_unittest_module(test_mock_shadows_r5, "mock_shadows_r5")
    n_pgl2 = test_pgl2_mellin_r5.run_all_tests()
    require(n_pgl2 == 3, f"Expected 3 pgl2_mellin test groups, got {n_pgl2}")
    n_sums = _run_unittest_module(test_sums_mixers_r5, "sums_mixers_r5")
    n_issues = _run_unittest_module(test_cli_and_issues_2_5_r5, "cli_and_issues_2_5_r5")

    # 3. CLI smoke checks (no disk side effects)
    buf_list = io.StringIO()
    with redirect_stdout(buf_list):
        rc_list = cli.main(["list"])
    require(rc_list == 0 and "pgl2_mellin" in buf_list.getvalue(), "CLI list check failed")

    buf_json = io.StringIO()
    with redirect_stdout(buf_json):
        rc_json = cli.main(["verify", "--module", "pgl2_mellin", "--json"])
    require(rc_json == 0, "CLI verify --json failed")
    parsed = json.loads(buf_json.getvalue())
    require(parsed["all_verified"] is True and parsed["modules_verified"] == 1, "CLI JSON output invalid")

    print("=== Foundation-0/ramanujan FULL VERIFICATION PASS ===")
    for key, info in bundle["receipts"].items():
        print(f"  [PASS] {key:14s}  sha256={info['canonical_sha256']}")
    print(f"  [PASS] mock_shadows R5 unittest: {n_mock}/{n_mock} tests")
    print(f"  [PASS] pgl2_mellin R5 suite:     {n_pgl2}/3 groups")
    print(f"  [PASS] sums_mixers R5 unittest:  {n_sums}/{n_sums} tests")
    print(f"  [PASS] issues #2-#5 R5 unittest: {n_issues}/{n_issues} tests")
    print(f"  Bundle SHA-256: {bundle['bundle_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
