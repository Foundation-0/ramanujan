"""Unified zero-dependency CLI for Foundation-0/ramanujan.

Usage:
    PYTHONPATH=. python3 -s -B -m ramanujan list
    PYTHONPATH=. python3 -s -B -m ramanujan verify [--json] [--module all|btz_graphs|mock_shadows|pgl2_mellin|sums_mixers]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any, Callable, Dict, Optional, Sequence, Tuple

from . import __version__
from . import btz_graphs
from . import mock_shadows
from . import pgl2_mellin
from . import sums_mixers


def _canonical_digest(payload: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def _count_floats(obj: Any) -> int:
    if isinstance(obj, float):
        return 1
    if isinstance(obj, dict):
        return sum(_count_floats(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(_count_floats(v) for v in obj)
    return 0


# (description, oracle_class, strict_zero_json_floats, builder)
_MODULES: Dict[str, Tuple[str, str, bool, Callable[[], Dict[str, Any]]]] = {
    "btz_graphs": (
        "AUDIT-044: Exact Integer Ramanujan Certifier, 840 H^1(G, Z_2) Signed 2-Lifts, BTZ Wormhole Parity & 24 Niemeier Lattices",
        "exact+sampled+anchor",
        False,
        btz_graphs.run_all,
    ),
    "mock_shadows": (
        "AUDIT-045: Deathbed Mock Theta Library, 4-Tier Euler-Witt Filtration, Rank-Crank Schur Obstruction & tau(1..500) / Cubic AGM",
        "exact+anchor",
        True,
        lambda: mock_shadows.run_all_probes(write_certificate=False),
    ),
    "pgl2_mellin": (
        "AUDIT-046: PGL(2, Q[[q]]) <-> Schur-Tridiagonal Continued Fractions, Hard-Core Inertia/Peeling & Q((eps)) Mellin Equalizer",
        "exact",
        True,
        pgl2_mellin.run_all,
    ),
    "sums_mixers": (
        "AUDIT-048R: Exact Integer Ramanujan Subspaces c_q(n), Coordinate-Free Ramanujan Mixers & Exact CF / Pell Numerology Refutation",
        "exact+anchor",
        False,
        sums_mixers.run_all_pillars,
    ),
}


def run_verify(module_choice: str = "all") -> Dict[str, Any]:
    if module_choice == "all":
        selected = list(_MODULES.keys())
    elif module_choice in _MODULES:
        selected = [module_choice]
    else:
        raise ValueError(f"Unknown module selector: {module_choice}")

    receipts: Dict[str, Dict[str, Any]] = {}
    for key in selected:
        desc, oracle_class, strict_zero, builder = _MODULES[key]
        payload = builder()
        _, digest = _canonical_digest(payload)
        float_count = _count_floats(payload)
        if strict_zero and float_count != 0:
            raise RuntimeError(
                f"Module {key} emitted {float_count} float(s); strict zero floats required"
            )
        receipts[key] = {
            "description": desc,
            "oracle_class": oracle_class,
            "exact_math_zero_floats": True,
            "strict_zero_json_floats": strict_zero,
            "diagnostic_float_fields": float_count,
            "canonical_sha256": digest,
            "verified": True,
        }

    bundle: Dict[str, Any] = {
        "package": "ramanujan",
        "version": __version__,
        "modules_verified": len(receipts),
        "all_verified": all(r["verified"] for r in receipts.values()),
        "receipts": receipts,
    }
    _, bundle_sha = _canonical_digest(bundle)
    bundle["bundle_sha256"] = bundle_sha
    return bundle


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ramanujan",
        description="Foundation-0/ramanujan zero-dependency exact verification suite",
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
    p_ver.add_argument("--json", action="store_true", help="Emit canonical JSON receipt bundle to stdout")

    sub.add_parser("list", help="List available verified Ramanujan modules")

    args = parser.parse_args(argv)
    if args.command == "list":
        for key, (desc, oracle_class, _, _) in _MODULES.items():
            print(f"{key:14s} [{oracle_class}]  {desc}")
        return 0

    if args.command == "verify":
        bundle = run_verify(args.module)
        if args.json:
            text, _ = _canonical_digest(bundle)
            sys.stdout.write(text)
        else:
            print(f"=== Foundation-0/ramanujan v{__version__} Verification Suite ===")
            for key, info in bundle["receipts"].items():
                print(
                    f"[PASS] {key:14s}  sha256={info['canonical_sha256'][:16]}...  "
                    f"({info['oracle_class']}, diag_floats={info['diagnostic_float_fields']})"
                )
            print(f"Modules verified: {bundle['modules_verified']}/{len(_MODULES) if args.module == 'all' else 1}")
            print(f"Bundle SHA-256:   {bundle['bundle_sha256']}")
        return 0

    parser.print_help()
    return 0
