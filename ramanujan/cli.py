"""Unified zero-dependency CLI for Foundation-0/ramanujan.

Usage:
    PYTHONPATH=. python3 -s -B -m ramanujan list
    PYTHONPATH=. python3 -s -B -m ramanujan verify [--json] [--exact-only] [--module all|btz_graphs|mock_shadows|pgl2_mellin|sums_mixers]
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from . import __version__


def _canonical_digest(payload: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def _count_floats(obj: Any) -> int:
    if type(obj) is float:
        return 1
    if type(obj) is dict:
        return sum(_count_floats(k) + _count_floats(v) for k, v in obj.items())
    if type(obj) in (list, tuple):
        return sum(_count_floats(v) for v in obj)
    return 0


def _build_btz(exact_only: bool = False) -> Dict[str, Any]:
    mod = importlib.import_module("ramanujan.btz_graphs")
    return mod.run_all(include_sampled=not exact_only)


def _build_mock(exact_only: bool = False) -> Dict[str, Any]:
    _ = exact_only
    mod = importlib.import_module("ramanujan.mock_shadows")
    return mod.run_all_probes(write_certificate=False)


def _build_pgl2(exact_only: bool = False) -> Dict[str, Any]:
    _ = exact_only
    mod = importlib.import_module("ramanujan.pgl2_mellin")
    return mod.run_all()


def _build_sums(exact_only: bool = False) -> Dict[str, Any]:
    _ = exact_only
    mod = importlib.import_module("ramanujan.sums_mixers")
    return mod.run_all_pillars()


# (description, oracle_class, strict_zero_json_floats, builder)
_MODULES: Dict[str, Tuple[str, str, bool, Callable[..., Dict[str, Any]]]] = {
    "btz_graphs": (
        "AUDIT-044: Exact Integer Ramanujan Certifier, 840 H^1(G, Z_2) Signed 2-Lifts, BTZ Wormhole Parity & 24 Niemeier Lattices (optional sampled Part C2)",
        "exact+sampled+anchor",
        False,
        _build_btz,
    ),
    "mock_shadows": (
        "AUDIT-045: Deathbed Mock Theta Library, 4-Tier Euler-Witt Filtration, Rank-Crank Schur Obstruction & tau(1..500) / Cubic AGM",
        "exact+anchor",
        True,
        _build_mock,
    ),
    "pgl2_mellin": (
        "AUDIT-046: PGL(2, Q[[q]]) <-> Schur-Tridiagonal Continued Fractions, Hard-Core Inertia/Peeling & Q((eps)) Mellin Equalizer",
        "exact",
        True,
        _build_pgl2,
    ),
    "sums_mixers": (
        "AUDIT-048R: Exact Integer Ramanujan Subspaces c_q(n), Coordinate-Free Ramanujan Mixers & Exact CF / Pell Numerology Refutation",
        "exact+anchor",
        False,
        _build_sums,
    ),
}


def _invoke_builder(builder: Callable[..., Dict[str, Any]], exact_only: bool) -> Dict[str, Any]:
    try:
        return builder(exact_only=exact_only)
    except TypeError:
        return builder()


def run_verify(module_choice: str = "all", *, exact_only: bool = False) -> Dict[str, Any]:
    if module_choice == "all":
        selected = list(_MODULES.keys())
    elif module_choice in _MODULES:
        selected = [module_choice]
    else:
        raise ValueError(f"Unknown module selector: {module_choice}")

    receipts: Dict[str, Dict[str, Any]] = {}
    for key in selected:
        desc, oracle_class, strict_zero, builder = _MODULES[key]
        payload = _invoke_builder(builder, exact_only=exact_only)
        if type(payload) is not dict:
            raise RuntimeError(f"Module {key} builder returned non-dict payload")
        _, digest = _canonical_digest(payload)
        float_count = _count_floats(payload)
        if strict_zero and float_count != 0:
            raise RuntimeError(
                f"Module {key} emitted {float_count} float(s); strict zero floats required"
            )
        # Fail-closed: every module MUST explicitly report all_passed is True.
        payload_passed = payload.get("all_passed") is True
        if "zero_floats_certified" in payload and payload["zero_floats_certified"] is not True:
            payload_passed = False

        effective_oracle = oracle_class
        if key == "btz_graphs":
            part_c = payload.get("part_c_niemeier_24_and_quantization")
            if type(part_c) is dict and part_c.get("sampled_benchmark_executed") is False:
                effective_oracle = "exact+anchor"

        zero_floats = float_count == 0
        receipts[key] = {
            "description": desc,
            "oracle_class": effective_oracle,
            "exact_math_zero_floats": zero_floats,
            "strict_zero_json_floats": strict_zero,
            "diagnostic_float_fields": float_count,
            "canonical_sha256": digest,
            "verified": payload_passed,
        }

    verified_count = sum(1 for r in receipts.values() if r["verified"] is True)
    all_verified = bool(receipts) and verified_count == len(receipts)
    bundle: Dict[str, Any] = {
        "package": "ramanujan",
        "version": __version__,
        "modules_verified": verified_count,
        "modules_selected": len(receipts),
        "all_verified": all_verified,
        "receipts": receipts,
    }
    _, bundle_sha = _canonical_digest(bundle)
    bundle["bundle_sha256"] = bundle_sha
    return bundle


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ramanujan",
        description="Foundation-0/ramanujan exact verification suite (pure-stdlib core; optional numpy for btz_graphs Part C2)",
    )
    parser.add_argument("--version", action="version", version=f"ramanujan {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_ver = sub.add_parser("verify", help="Run verified Ramanujan modules and emit SHA-256 receipts")
    p_ver.add_argument(
        "--module",
        choices=["all", "btz_graphs", "mock_shadows", "pgl2_mellin", "sums_mixers"],
        default="all",
        help="Module to verify (default: all)",
    )
    p_ver.add_argument(
        "--exact-only",
        action="store_true",
        help="Skip optional numpy float64 Part C2 benchmark in btz_graphs",
    )
    p_ver.add_argument("--json", action="store_true", help="Emit canonical JSON receipt bundle to stdout")

    sub.add_parser("list", help="List available verified Ramanujan modules")

    args = parser.parse_args(argv)
    if args.command == "list":
        for key, (desc, oracle_class, _, _) in _MODULES.items():
            print(f"{key:14s} [{oracle_class}]  {desc}")
        return 0

    if args.command == "verify":
        bundle = run_verify(args.module, exact_only=args.exact_only)
        if args.json:
            text, _ = _canonical_digest(bundle)
            sys.stdout.write(text)
        else:
            print(f"=== Foundation-0/ramanujan v{__version__} Verification Suite ===")
            for key, info in bundle["receipts"].items():
                tag = "PASS" if info["verified"] else "FAIL"
                print(
                    f"[{tag}] {key:14s}  sha256={info['canonical_sha256'][:16]}...  "
                    f"({info['oracle_class']}, diag_floats={info['diagnostic_float_fields']})"
                )
            print(f"Modules verified: {bundle['modules_verified']}/{bundle['modules_selected']}")
            print(f"Bundle SHA-256:   {bundle['bundle_sha256']}")
        return 0 if bundle["all_verified"] else 1

    parser.print_help()
    return 0
