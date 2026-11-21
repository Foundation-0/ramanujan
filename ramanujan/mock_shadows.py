#!/usr/bin/env python3
"""Round 4 Arm R4-2 (AUDIT-045): Ramanujan Mock Modular Shadows, Rank-Crank
Schur Obstructions, 4-Tier Exact Integer Hankel/Euler-Witt Filtration,
Tau(n) / Cubic-Theta AGM, and Live aletheia v1.2.0 3-Lab Lean 4 Forensics.

100% pure Python 3 stdlib (int + fractions.Fraction). ZERO floating-point
arithmetic anywhere in theorems or emitted JSON. ZERO bare assert statements.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


# ============================================================================
# Strict R3 Validation & Exact Scalar Helpers (Zero Floats, Zero Bare Asserts)
# ============================================================================

def require_exact_int(val: Any, name: str) -> int:
    """Strictly require an exact Python int (rejecting bool, float, str)."""
    if isinstance(val, bool) or not isinstance(val, int):
        raise TypeError(f"{name} must be an exact int (got {type(val).__name__})")
    return val


def require_exact_rational(val: Any, name: str) -> Fraction:
    """Strictly convert exact int or Fraction (rejecting bool, float, str)."""
    if isinstance(val, bool) or not isinstance(val, (int, Fraction)):
        raise TypeError(f"{name} must be exact int or Fraction (got {type(val).__name__})")
    return Fraction(val)


def frac_str(x: Fraction) -> str:
    """Canonical exact rational string 'p/q' (or 'p' if integer)."""
    f = require_exact_rational(x, "x")
    return f"{f.numerator}" if f.denominator == 1 else f"{f.numerator}/{f.denominator}"


def ceil_fraction(x: Fraction) -> int:
    """Exact integer ceiling of a Fraction without floats."""
    f = require_exact_rational(x, "x")
    return -((-f.numerator) // f.denominator)


def verify_no_floats(obj: Any, path: str = "$") -> None:
    """Recursively fail closed if any float appears anywhere in a JSON structure."""
    if isinstance(obj, float):
        raise ValueError(f"Forbidden float detected at {path}: {obj!r}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            verify_no_floats(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for idx, v in enumerate(obj):
            verify_no_floats(v, f"{path}[{idx}]")


# ============================================================================
# Part 1: Exact Z[[q]] / Q[[q]] Power-Series Engine & Mock Theta Library
# ============================================================================

def q_add(a: list[int], b: list[int], n_terms: int) -> list[int]:
    return [a[i] + b[i] for i in range(n_terms)]


def q_sub(a: list[int], b: list[int], n_terms: int) -> list[int]:
    return [a[i] - b[i] for i in range(n_terms)]


def q_scale(c: int, a: list[int], n_terms: int) -> list[int]:
    c_int = require_exact_int(c, "c")
    return [c_int * a[i] for i in range(n_terms)]


def q_mul(a: list[int], b: list[int], n_terms: int) -> list[int]:
    out = [0] * n_terms
    for i in range(n_terms):
        ai = a[i]
        if ai:
            for j in range(n_terms - i):
                out[i + j] += ai * b[j]
    return out


def q_pow(a: list[int], exp: int, n_terms: int) -> list[int]:
    e = require_exact_int(exp, "exp")
    if e < 0:
        raise ValueError("exp must be non-negative")
    res = [0] * n_terms
    res[0] = 1
    base = a[:n_terms]
    while e > 0:
        if e & 1:
            res = q_mul(res, base, n_terms)
        base = q_mul(base, base, n_terms)
        e >>= 1
    return res


def q_inv_unit(a: list[int], n_terms: int) -> list[int]:
    """Exact inverse in Z[[q]] requiring constant term in {+1, -1}."""
    if not a or a[0] not in (1, -1):
        raise ValueError(f"q_inv_unit requires constant term in {{1, -1}} (got {a[0] if a else None})")
    s = a[0]
    out = [0] * n_terms
    out[0] = s
    for n in range(1, n_terms):
        acc = 0
        for k in range(1, n + 1):
            ak = a[k]
            if ak:
                acc += ak * out[n - k]
        out[n] = -s * acc
    return out


def q_neg(a: list[int], n_terms: int) -> list[int]:
    """Return a(-q)."""
    return [a[i] if (i & 1) == 0 else -a[i] for i in range(n_terms)]


def q_sub_pow(a: list[int], m: int, n_terms: int) -> list[int]:
    """Return a(q^m)."""
    m_int = require_exact_int(m, "m")
    if m_int <= 0:
        raise ValueError("m must be a positive integer")
    out = [0] * n_terms
    for i in range(n_terms):
        idx = i * m_int
        if idx >= n_terms:
            break
        out[idx] = a[i]
    return out


def q_shift(a: list[int], k: int, n_terms: int) -> list[int]:
    """Return q^k * a(q) truncated to n_terms (k >= 0)."""
    k_int = require_exact_int(k, "k")
    if k_int < 0:
        raise ValueError("k must be non-negative")
    if k_int >= n_terms:
        return [0] * n_terms
    return [0] * k_int + a[: n_terms - k_int]


def q_theta_deriv(a: list[int], n_terms: int) -> list[int]:
    """Return D(a) = q * d/dq a(q) = sum n * a_n * q^n."""
    return [i * a[i] for i in range(n_terms)]


def poch_finite(sign_a: int, pow_a: int, step: int, count: int, n_terms: int) -> list[int]:
    """Exact prod_{k=0}^{count-1} (1 - sign_a * q^{pow_a + k*step}) in Z[[q]]."""
    if sign_a not in (1, -1):
        raise ValueError("sign_a must be +1 or -1")
    if pow_a < 1 or step < 1 or count < 0:
        raise ValueError("poch_finite requires pow_a >= 1, step >= 1, count >= 0")
    res = [0] * n_terms
    res[0] = 1
    for k in range(count):
        e = pow_a + k * step
        if e >= n_terms:
            break
        for i in range(n_terms - 1, e - 1, -1):
            res[i] -= sign_a * res[i - e]
    return res


def poch_inf(sign_a: int, pow_a: int, step: int, n_terms: int) -> list[int]:
    """Exact prod_{k>=0} (1 - sign_a * q^{pow_a + k*step}) truncated to n_terms."""
    if sign_a not in (1, -1):
        raise ValueError("sign_a must be +1 or -1")
    if pow_a < 1 or step < 1:
        raise ValueError("poch_inf requires pow_a >= 1, step >= 1")
    res = [0] * n_terms
    res[0] = 1
    e = pow_a
    while e < n_terms:
        for i in range(n_terms - 1, e - 1, -1):
            res[i] -= sign_a * res[i - e]
        e += step
    return res


def q_mul_frac(a: list[Fraction], b: list[Fraction], n_terms: int) -> list[Fraction]:
    out = [Fraction(0)] * n_terms
    for i in range(n_terms):
        ai = a[i]
        if ai:
            for j in range(n_terms - i):
                out[i + j] += ai * b[j]
    return out


def q_inv_frac(a: list[Fraction], n_terms: int) -> list[Fraction]:
    if not a or a[0] == 0:
        raise ValueError("q_inv_frac requires nonzero constant term")
    a0 = a[0]
    out = [Fraction(0)] * n_terms
    out[0] = Fraction(1) / a0
    for n in range(1, n_terms):
        acc = Fraction(0)
        for k in range(1, n + 1):
            if a[k]:
                acc += a[k] * out[n - k]
        out[n] = -acc / a0
    return out


def poch_frac(sign_z: int, pow_z: int, step: int, count: int, n_terms: int) -> list[Fraction]:
    """Exact prod_{k=0}^{count-1} (1 - sign_z * q^{pow_z + k*step}) in Q[[q]], allowing pow_z==0 when sign_z==-1."""
    if sign_z not in (1, -1):
        raise ValueError("sign_z must be +1 or -1")
    res = [Fraction(0)] * n_terms
    res[0] = Fraction(1)
    for k in range(count):
        e = pow_z + k * step
        if e >= n_terms:
            break
        if e == 0:
            fac = 1 - sign_z
            if fac == 0:
                raise ValueError("Zero constant factor (1 - 1) encountered in poch_frac")
            res = [x * fac for x in res]
        else:
            for i in range(n_terms - 1, e - 1, -1):
                res[i] -= sign_z * res[i - e]
    return res


def universal_g3(sign_z: int, a_pow: int, base_step: int, n_terms: int) -> list[Fraction]:
    """Gordon-McIntosh universal mock theta g3(sign_z * q^{a_pow}; q^{base_step})."""
    out = [Fraction(0)] * n_terms
    for n in range(n_terms):
        e = base_step * n * (n + 1)
        if e >= n_terms:
            break
        d1 = poch_frac(sign_z, a_pow, base_step, n + 1, n_terms)
        d2 = poch_frac(sign_z, base_step - a_pow, base_step, n + 1, n_terms)
        invd = q_inv_frac(q_mul_frac(d1, d2, n_terms), n_terms)
        for i in range(n_terms - e):
            out[i + e] += invd[i]
    return out


def universal_g2(sign_z: int, a_pow: int, base_step: int, n_terms: int) -> list[Fraction]:
    """Gordon-McIntosh universal mock theta g2(sign_z * q^{a_pow}; q^{base_step})."""
    out = [Fraction(0)] * n_terms
    for n in range(n_terms):
        e = base_step * n * (n + 1) // 2
        if e >= n_terms:
            break
        num = poch_frac(-1, base_step, base_step, n, n_terms)
        d1 = poch_frac(sign_z, a_pow, base_step, n + 1, n_terms)
        d2 = poch_frac(sign_z, base_step - a_pow, base_step, n + 1, n_terms)
        term = q_mul_frac(num, q_inv_frac(q_mul_frac(d1, d2, n_terms), n_terms), n_terms)
        for i in range(n_terms - e):
            out[i + e] += term[i]
    return out


def sigma_pow(n: int, k: int) -> int:
    """Exact divisor power sum sigma_k(n)."""
    total = 0
    lim = math.isqrt(n)
    for d in range(1, lim + 1):
        if n % d == 0:
            total += d ** k
            q = n // d
            if q != d:
                total += q ** k
    return total


def build_q_series_library(n_terms: int = 70) -> dict[str, list[int]]:
    """Construct complete exact integer library of modular, quasimodular,
    3rd/5th/7th-order mock theta, false theta, and partial theta q-series.
    """
    n_int = require_exact_int(n_terms, "n_terms")
    if n_int < 30:
        raise ValueError("n_terms must be at least 30")

    eta1 = poch_inf(1, 1, 1, n_int)
    eta2 = poch_inf(1, 2, 2, n_int)
    neg_q_inf = poch_inf(-1, 1, 1, n_int)
    p_ser = q_inv_unit(eta1, n_int)
    delta_q = q_pow(eta1, 24, n_int)

    theta3 = [0] * n_int
    theta4 = [0] * n_int
    partial_theta = [0] * n_int
    theta3[0] = 1
    theta4[0] = 1
    partial_theta[0] = 1
    for k in range(1, math.isqrt(n_int - 1) + 1):
        sq = k * k
        theta3[sq] = 2
        theta4[sq] = 2 if (k & 1) == 0 else -2
        partial_theta[sq] = 1

    # Andrews-Garvan crank at z = -1: (q;q)_inf / (-q;q)_inf^2 == theta4(q)^2 / (q;q)_inf
    crank_neg1 = q_mul(eta1, q_inv_unit(q_mul(neg_q_inf, neg_q_inf, n_int), n_int), n_int)

    # Eisenstein series (modular E4, E6; quasimodular E2)
    e2 = [1] + [-24 * sigma_pow(n, 1) for n in range(1, n_int)]
    e4 = [1] + [240 * sigma_pow(n, 3) for n in range(1, n_int)]
    e6 = [1] + [-504 * sigma_pow(n, 5) for n in range(1, n_int)]

    # False theta functions
    false_tri = [0] * n_int
    k = 0
    while k * (k + 1) // 2 < n_int:
        false_tri[k * (k + 1) // 2] = 1 if (k & 1) == 0 else -1
        k += 1

    # Rogers/Ramanujan false pentagonal: sign-flipped negative branch vs Euler pentagonal
    false_pent = [0] * n_int
    k = 0
    while True:
        e1 = k * (3 * k + 1) // 2
        e2_idx = (k + 1) * (3 * k + 2) // 2
        if e1 >= n_int and e2_idx >= n_int:
            break
        s = 1 if (k & 1) == 0 else -1
        if e1 < n_int:
            false_pent[e1] += s
        if e2_idx < n_int:
            false_pent[e2_idx] += s
        k += 1

    # Rational control: 1 / (1 - q - q^2) (Fibonacci generating function, Hankel rank 2)
    fib_rat = [0] * n_int
    fib_rat[0] = 1
    fib_rat[1] = 1
    for i in range(2, n_int):
        fib_rat[i] = fib_rat[i - 1] + fib_rat[i - 2]

    # --- 3rd-order Ramanujan mock thetas (all 7) ---
    m3_f = [0] * n_int
    m3_phi = [0] * n_int
    m3_psi = [0] * n_int
    m3_chi = [0] * n_int
    m3_omega = [0] * n_int
    m3_nu = [0] * n_int
    m3_rho = [0] * n_int
    for n in range(n_int):
        sq = n * n
        if sq < n_int:
            d_f = poch_finite(-1, 1, 1, n, n_int)
            t_f = q_inv_unit(q_mul(d_f, d_f, n_int), n_int)
            t_phi = q_inv_unit(poch_finite(-1, 2, 2, n, n_int), n_int)
            t_chi = q_mul(d_f, q_inv_unit(poch_finite(-1, 3, 3, n, n_int), n_int), n_int)
            for i in range(n_int - sq):
                m3_f[i + sq] += t_f[i]
                m3_phi[i + sq] += t_phi[i]
                m3_chi[i + sq] += t_chi[i]
            if n >= 1:
                t_psi = q_inv_unit(poch_finite(1, 1, 2, n, n_int), n_int)
                for i in range(n_int - sq):
                    m3_psi[i + sq] += t_psi[i]
        e_nu = n * n + n
        if e_nu < n_int:
            t_nu = q_inv_unit(poch_finite(-1, 1, 2, n + 1, n_int), n_int)
            for i in range(n_int - e_nu):
                m3_nu[i + e_nu] += t_nu[i]
        e_om = 2 * n * n + 2 * n
        if e_om < n_int:
            d_om = poch_finite(1, 1, 2, n + 1, n_int)
            t_om = q_inv_unit(q_mul(d_om, d_om, n_int), n_int)
            t_rho = q_mul(d_om, q_inv_unit(poch_finite(1, 3, 6, n + 1, n_int), n_int), n_int)
            for i in range(n_int - e_om):
                m3_omega[i + e_om] += t_om[i]
                m3_rho[i + e_om] += t_rho[i]

    # --- 5th-order Ramanujan mock thetas (all 10: 0-family & 1-family) ---
    m5_f0 = [0] * n_int
    m5_F0 = [0] * n_int
    m5_phi0 = [0] * n_int
    m5_psi0 = [0] * n_int
    m5_chi0 = [0] * n_int
    m5_f1 = [0] * n_int
    m5_F1 = [0] * n_int
    m5_phi1 = [0] * n_int
    m5_psi1 = [0] * n_int
    m5_chi1 = [0] * n_int
    for n in range(n_int):
        sq = n * n
        if sq < n_int:
            t_f0 = q_inv_unit(poch_finite(-1, 1, 1, n, n_int), n_int)
            t_phi0 = poch_finite(-1, 1, 2, n, n_int)
            for i in range(n_int - sq):
                m5_f0[i + sq] += t_f0[i]
                m5_phi0[i + sq] += t_phi0[i]
        e_2sq = 2 * n * n
        if e_2sq < n_int:
            t_F0 = q_inv_unit(poch_finite(1, 1, 2, n, n_int), n_int)
            for i in range(n_int - e_2sq):
                m5_F0[i + e_2sq] += t_F0[i]
        e_tri1 = (n + 1) * (n + 2) // 2
        if e_tri1 < n_int:
            t_psi0 = poch_finite(-1, 1, 1, n, n_int)
            for i in range(n_int - e_tri1):
                m5_psi0[i + e_tri1] += t_psi0[i]
        t_chi0 = q_inv_unit(poch_finite(1, n + 1, 1, n, n_int), n_int)
        t_chi1 = q_inv_unit(poch_finite(1, n + 1, 1, n + 1, n_int), n_int)
        for i in range(n_int - n):
            m5_chi0[i + n] += t_chi0[i]
            m5_chi1[i + n] += t_chi1[i]
        e_f1 = n * n + n
        if e_f1 < n_int:
            t_f1 = q_inv_unit(poch_finite(-1, 1, 1, n, n_int), n_int)
            for i in range(n_int - e_f1):
                m5_f1[i + e_f1] += t_f1[i]
        e_F1 = 2 * n * n + 2 * n
        if e_F1 < n_int:
            t_F1 = q_inv_unit(poch_finite(1, 1, 2, n + 1, n_int), n_int)
            for i in range(n_int - e_F1):
                m5_F1[i + e_F1] += t_F1[i]
        e_phi1 = (n + 1) * (n + 1)
        if e_phi1 < n_int:
            t_phi1 = poch_finite(-1, 1, 2, n, n_int)
            for i in range(n_int - e_phi1):
                m5_phi1[i + e_phi1] += t_phi1[i]
        e_tri0 = n * (n + 1) // 2
        if e_tri0 < n_int:
            t_psi1 = poch_finite(-1, 1, 1, n, n_int)
            for i in range(n_int - e_tri0):
                m5_psi1[i + e_tri0] += t_psi1[i]

    # --- 7th-order Ramanujan mock thetas (all 3) ---
    m7_F0 = [0] * n_int
    m7_F1 = [0] * n_int
    m7_F2 = [0] * n_int
    for n in range(n_int):
        sq = n * n
        if sq < n_int:
            t0 = q_inv_unit(poch_finite(1, n + 1, 1, n, n_int), n_int)
            for i in range(n_int - sq):
                m7_F0[i + sq] += t0[i]
            if n >= 1:
                t1 = q_inv_unit(poch_finite(1, n, 1, n, n_int), n_int)
                for i in range(n_int - sq):
                    m7_F1[i + sq] += t1[i]
        e2_7 = n * n + n
        if e2_7 < n_int:
            t2 = q_inv_unit(poch_finite(1, n + 1, 1, n + 1, n_int), n_int)
            for i in range(n_int - e2_7):
                m7_F2[i + e2_7] += t2[i]

    return {
        "rational_fib": fib_rat,
        "eta1": eta1,
        "eta2": eta2,
        "p_ser": p_ser,
        "delta_q": delta_q,
        "theta3": theta3,
        "theta4": theta4,
        "crank_neg1": crank_neg1,
        "E2": e2,
        "E4": e4,
        "E6": e6,
        "partial_theta": partial_theta,
        "false_tri": false_tri,
        "false_pent": false_pent,
        "m3_f": m3_f,
        "m3_phi": m3_phi,
        "m3_psi": m3_psi,
        "m3_chi": m3_chi,
        "m3_omega": m3_omega,
        "m3_nu": m3_nu,
        "m3_rho": m3_rho,
        "m5_f0": m5_f0,
        "m5_F0": m5_F0,
        "m5_phi0": m5_phi0,
        "m5_psi0": m5_psi0,
        "m5_chi0": m5_chi0,
        "m5_f1": m5_f1,
        "m5_F1": m5_F1,
        "m5_phi1": m5_phi1,
        "m5_psi1": m5_psi1,
        "m5_chi1": m5_chi1,
        "m7_F0": m7_F0,
        "m7_F1": m7_F1,
        "m7_F2": m7_F2,
    }


def verify_mock_theta_and_appell_lerch_identities(lib: dict[str, list[int]], n_terms: int) -> dict[str, Any]:
    """Verify exact 3rd/5th-order Watson-Ramanujan identities, Gordon-McIntosh
    universal mock theta g3/g2 specializations, and bilateral Appell-Lerch sums.
    """
    eta1 = lib["eta1"]
    eta2 = lib["eta2"]
    theta4 = lib["theta4"]
    crank_neg1 = lib["crank_neg1"]
    f3 = lib["m3_f"]
    phi3 = lib["m3_phi"]
    psi3 = lib["m3_psi"]
    omega3 = lib["m3_omega"]

    # 1. Crank z=-1 == theta4(q)^2 / (q;q)_inf
    theta4_sq_over_eta = q_mul(q_mul(theta4, theta4, n_terms), q_inv_unit(eta1, n_terms), n_terms)
    id_crank_theta4 = crank_neg1 == theta4_sq_over_eta

    # 2. 3rd-order Watson-Ramanujan identities
    id_m3_f_psi = q_add(f3, q_scale(4, q_neg(psi3, n_terms), n_terms), n_terms) == crank_neg1
    id_m3_phi_f = q_sub(q_scale(2, q_neg(phi3, n_terms), n_terms), f3, n_terms) == crank_neg1

    # 3. 5th-order Watson-Ramanujan identities
    id_m5_chi0 = lib["m5_chi0"] == q_sub(q_scale(2, lib["m5_F0"], n_terms), q_neg(lib["m5_phi0"], n_terms), n_terms)
    phi1_neg_div_q = q_neg(lib["m5_phi1"], n_terms)[1:]
    id_m5_chi1 = lib["m5_chi1"][:-1] == [2 * lib["m5_F1"][i] + phi1_neg_div_q[i] for i in range(n_terms - 1)]

    phi0_neg_q2 = [0] * n_terms
    for i in range(n_terms):
        if 2 * i < n_terms:
            phi0_neg_q2[2 * i] = lib["m5_phi0"][i] if (i & 1) == 0 else -lib["m5_phi0"][i]
    lhs_m5_0 = [lib["m5_f0"][i] + 2 * q_sub_pow(lib["m5_F0"], 2, n_terms)[i] - (2 if i == 0 else 0) for i in range(n_terms)]
    rhs_m5_0 = q_add(phi0_neg_q2, lib["m5_psi0"], n_terms)
    id_m5_f0_F0_phi0_psi0 = lhs_m5_0 == rhs_m5_0

    # 4. Universal mock theta g3 & g2 specializations (N = 50 exact Fraction)
    k_uni = min(50, n_terms)
    g3_m1 = universal_g3(-1, 0, 1, k_uni)
    id_g3_f = [Fraction(f3[i]) for i in range(k_uni)] == [
        (Fraction(2) if i == 0 else Fraction(0)) - 2 * g3_m1[i] for i in range(k_uni)
    ]
    g3_q_q2 = universal_g3(1, 1, 2, k_uni)
    id_g3_omega = [Fraction(omega3[i]) for i in range(k_uni)] == g3_q_q2

    # 2nd-order mock theta B(q) = sum_{n>=0} q^n (-q; q^2)_n / (q; q^2)_{n+1} == g2(q; q^2)?
    # Check exact Gordon-McIntosh identity: sum_{n>=0} (-q;q^2)_n q^{n(n+1)} / (q^2;q^2)_n?
    # Even cleaner: Gordon-McIntosh 2nd-order mu(q) = sum_{n>=0} (-1)^n q^{n^2} (q; q^2)_n / (-q^2; q^2)_n^2
    # Wait: verify g2(-1; q) exact integer-scaled series 2*g2(-1; q) has pure integer coeffs (2nd-order A(q)/mu(q) relation)
    g2_m1 = universal_g2(-1, 0, 1, k_uni)
    two_g2_m1_int = all((2 * x).denominator == 1 for x in g2_m1)

    # 5. Exact Bilateral Appell-Lerch representations (Watson 1936 / Zwegers 2002)
    # (q;q)_inf * f(q) == 1 + 4 * sum_{n>=1} (-1)^n q^{n(3n+1)/2} / (1 + q^n)
    al_f = [0] * n_terms
    al_f[0] = 1
    n = 1
    while n * (3 * n + 1) // 2 < n_terms:
        e = n * (3 * n + 1) // 2
        s = 4 if (n & 1) == 0 else -4
        k = 0
        while e + k * n < n_terms:
            al_f[e + k * n] += s if (k & 1) == 0 else -s
            k += 1
        n += 1
    id_appell_lerch_f = q_mul(eta1, f3, n_terms) == al_f

    # (q^2;q^2)_inf * omega(q) == sum_{n>=0} (-1)^n q^{3n^2+3n} (1 + q^{2n+1}) / (1 - q^{2n+1})
    al_om = [0] * n_terms
    n = 0
    while 3 * n * n + 3 * n < n_terms:
        e = 3 * n * n + 3 * n
        s = 1 if (n & 1) == 0 else -1
        step = 2 * n + 1
        al_om[e] += s
        k = 1
        while e + k * step < n_terms:
            al_om[e + k * step] += 2 * s
            k += 1
        n += 1
    id_appell_lerch_omega = q_mul(eta2, omega3, n_terms) == al_om

    checks = {
        "crank_neg1_eq_theta4_sq_over_eta": id_crank_theta4,
        "mock3_f_plus_4psi_neg_eq_crank_neg1": id_m3_f_psi,
        "mock3_2phi_neg_minus_f_eq_crank_neg1": id_m3_phi_f,
        "mock5_chi0_eq_2F0_minus_phi0_neg": id_m5_chi0,
        "mock5_chi1_eq_2F1_plus_qinv_phi1_neg": id_m5_chi1,
        "mock5_f0_plus_2F0_q2_minus_2_eq_phi0_neg_q2_plus_psi0": id_m5_f0_F0_phi0_psi0,
        "universal_g3_f_eq_2_minus_2g3_neg1": id_g3_f,
        "universal_g3_omega_eq_g3_q_q2": id_g3_omega,
        "universal_2g2_neg1_integer_coeffs": two_g2_m1_int,
        "appell_lerch_eta_f": id_appell_lerch_f,
        "appell_lerch_eta2_omega": id_appell_lerch_omega,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Mock theta / Appell-Lerch identity check failed: {checks}")

    return {
        "truncation_order": n_terms,
        "universal_truncation_order": k_uni,
        "identities_all_verified": True,
        "checks": checks,
        "sample_coeffs_first_12": {
            "m3_f": f3[:12],
            "m3_omega": omega3[:12],
            "m5_f0": lib["m5_f0"][:12],
            "m7_F0": lib["m7_F0"][:12],
            "m7_F1": lib["m7_F1"][:12],
            "m7_F2": lib["m7_F2"][:12],
            "crank_neg1": crank_neg1[:12],
            "two_g2_neg1": [int(2 * x) for x in g2_m1[:12]],
        },
    }


# ============================================================================
# Part 2: Exact Linear Algebra (Bunch-Kaufman Inertia, Bareiss PSD,
#         Euler-Witt Transform, R_opt & R_H4, 4-Tier Filtration)
# ============================================================================

def exact_symmetric_inertia(mat: list[list[int | Fraction]]) -> tuple[int, int, int]:
    """Exact (n_pos, n_zero, n_neg) inertia of a symmetric rational matrix
    via exact 1x1 / 2x2 Bunch-Kaufman rational congruence over Q.
    Strictly validates symmetry and non-empty square dimensions.
    """
    if not isinstance(mat, list) or not mat:
        raise ValueError("Matrix must be a non-empty list of rows")
    m = len(mat)
    A: list[list[Fraction]] = []
    for r_idx, row in enumerate(mat):
        if not isinstance(row, list) or len(row) != m:
            raise ValueError(f"Matrix row {r_idx} does not match square dimension {m}")
        A.append([require_exact_rational(x, f"mat[{r_idx}][{c_idx}]") for c_idx, x in enumerate(row)])
    for i in range(m):
        for j in range(i + 1, m):
            if A[i][j] != A[j][i]:
                raise ValueError(f"Matrix is not symmetric at ({i},{j}): {A[i][j]} != {A[j][i]}")

    n_pos = 0
    n_neg = 0
    n_zero = 0
    i = 0
    while i < m:
        piv = None
        for r in range(i, m):
            if A[r][r] != 0:
                piv = r
                break
        if piv is not None:
            if piv != i:
                A[i], A[piv] = A[piv], A[i]
                for row in A:
                    row[i], row[piv] = row[piv], row[i]
            d = A[i][i]
            if d > 0:
                n_pos += 1
            else:
                n_neg += 1
            for r in range(i + 1, m):
                if A[r][i] != 0:
                    fac = A[r][i] / d
                    for c in range(i + 1, m):
                        A[r][c] -= fac * A[i][c]
                    A[r][i] = Fraction(0)
            i += 1
        else:
            pair = None
            for r in range(i, m):
                for c in range(r + 1, m):
                    if A[r][c] != 0:
                        pair = (r, c)
                        break
                if pair is not None:
                    break
            if pair is None:
                n_zero += m - i
                break
            r, c = pair
            if r != i:
                A[i], A[r] = A[r], A[i]
                for row in A:
                    row[i], row[r] = row[r], row[i]
                if c == i:
                    c = r
            if c != i + 1:
                A[i + 1], A[c] = A[c], A[i + 1]
                for row in A:
                    row[i + 1], row[c] = row[c], row[i + 1]
            b = A[i][i + 1]
            n_pos += 1
            n_neg += 1
            for r2 in range(i + 2, m):
                u = A[r2][i]
                v = A[r2][i + 1]
                if u != 0 or v != 0:
                    fu = v / b
                    fv = u / b
                    for c2 in range(i + 2, m):
                        A[r2][c2] -= fu * A[i][c2] + fv * A[i + 1][c2]
                    A[r2][i] = Fraction(0)
                    A[r2][i + 1] = Fraction(0)
            i += 2
    return (n_pos, n_zero, n_neg)


def exact_bareiss_leading_minors(mat: list[list[int | Fraction]]) -> list[Fraction]:
    """Compute exact leading principal minors det(M[:k, :k]) for k=1..m over Q."""
    m = len(mat)
    minors: list[Fraction] = []
    for k in range(1, m + 1):
        sub = [[require_exact_rational(mat[i][j], "entry") for j in range(k)] for i in range(k)]
        det = Fraction(1)
        for col in range(k):
            piv = None
            for row in range(col, k):
                if sub[row][col] != 0:
                    piv = row
                    break
            if piv is None:
                det = Fraction(0)
                break
            if piv != col:
                sub[col], sub[piv] = sub[piv], sub[col]
                det = -det
            d = sub[col][col]
            det *= d
            for row in range(col + 1, k):
                if sub[row][col] != 0:
                    fac = sub[row][col] / d
                    for j in range(col + 1, k):
                        sub[row][j] -= fac * sub[col][j]
        minors.append(det)
    return minors


def exact_col_rank(mat: list[list[int | Fraction]]) -> int:
    """Exact column/row rank of a rectangular matrix over Q."""
    if not mat or not mat[0]:
        return 0
    m = len(mat)
    n = len(mat[0])
    A = [[require_exact_rational(mat[i][j], "entry") for j in range(n)] for i in range(m)]
    r = 0
    for c in range(n):
        piv = next((i for i in range(r, m) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        d = A[r][c]
        A[r] = [x / d for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
    return r


def mat_mul_frac(A: list[list[Fraction]], B: list[list[Fraction]]) -> list[list[Fraction]]:
    m = len(A)
    k = len(B)
    n = len(B[0])
    return [
        [sum((A[i][t] * B[t][j] for t in range(k)), Fraction(0)) for j in range(n)]
        for i in range(m)
    ]


def mat_transpose_frac(A: list[list[Fraction]]) -> list[list[Fraction]]:
    m = len(A)
    n = len(A[0])
    return [[A[i][j] for i in range(m)] for j in range(n)]


def exact_pinv_symmetric_psd(G: list[list[Fraction]]) -> list[list[Fraction]]:
    """Exact Moore-Penrose pseudoinverse G^+ for a symmetric PSD rational matrix G
    via exact column-basis Gram factorization G = B B^T? Better: full-rank column subset
    C of G (since G is symmetric PSD, col(G) has basis C = G[:, piv], and G = C M^{-1} C^T
    where M = G[piv, piv] is strictly invertible, hence G^+ = C (C^T C)^{-1} M (C^T C)^{-1} C^T!).
    Verified directly against all 4 Moore-Penrose axioms before returning.
    """
    m = len(G)
    # Find linearly independent pivot indices via RREF
    A = [row[:] for row in G]
    pivots: list[int] = []
    r = 0
    for c in range(m):
        piv = next((i for i in range(r, m) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        d = A[r][c]
        A[r] = [x / d for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(m)]
        pivots.append(c)
        r += 1
    if not pivots:
        return [[Fraction(0)] * m for _ in range(m)]

    # Invertible square matrix helper over Q
    def inv_square(S: list[list[Fraction]]) -> list[list[Fraction]]:
        k = len(S)
        aug = [S[i][:] + [Fraction(1 if i == j else 0) for j in range(k)] for i in range(k)]
        for col in range(k):
            p = next((row for row in range(col, k) if aug[row][col] != 0), None)
            if p is None:
                raise ValueError("Singular matrix in inv_square")
            aug[col], aug[p] = aug[p], aug[col]
            d = aug[col][col]
            aug[col] = [x / d for x in aug[col]]
            for row in range(k):
                if row != col and aug[row][col] != 0:
                    f = aug[row][col]
                    aug[row] = [aug[row][j] - f * aug[col][j] for j in range(2 * k)]
        return [row[k:] for row in aug]

    # C is m x r (columns of G at pivot indices); M = G[pivots, pivots] (r x r invertible)
    # Since G is symmetric and col(G)=col(C), G = C M^{-1} C^T.
    # For any full-column-rank C and symmetric invertible M, (C M^{-1} C^T)^+ = C (C^T C)^{-1} M (C^T C)^{-1} C^T!
    C = [[G[i][j] for j in pivots] for i in range(m)]
    CT = mat_transpose_frac(C)
    CTC = mat_mul_frac(CT, C)
    CTC_inv = inv_square(CTC)
    M = [[G[i][j] for j in pivots] for i in pivots]
    mid = mat_mul_frac(mat_mul_frac(CTC_inv, M), CTC_inv)
    G_pinv = mat_mul_frac(mat_mul_frac(C, mid), CT)

    # Verify all 4 Moore-Penrose axioms explicitly!
    GGp = mat_mul_frac(G, G_pinv)
    GpG = mat_mul_frac(G_pinv, G)
    if mat_mul_frac(GGp, G) != G:
        raise RuntimeError("Moore-Penrose axiom 1 (G G^+ G == G) failed")
    if mat_mul_frac(GpG, G_pinv) != G_pinv:
        raise RuntimeError("Moore-Penrose axiom 2 (G^+ G G^+ == G^+) failed")
    if GGp != mat_transpose_frac(GGp) or GpG != mat_transpose_frac(GpG):
        raise RuntimeError("Moore-Penrose symmetry axioms 3/4 failed")
    return G_pinv


def psd_r_opt_and_r_h4(gram_psd: list[list[Fraction]]) -> dict[str, Any]:
    """Exact rational spectral lower bounds on rank(M) for PSD M >= 0:
    - R_opt (AUDIT-002, b=0): (tr M)^2 / tr(M^2) <= rank(M)
    - R_H4  (AUDIT-014 2-step Schur moment bound on 3x3 Hankel [[r, t1, t2], [t1, t2, t3], [t2, t3, t4]] >= 0):
        (t1^2 t4 - 2 t1 t2 t3 + t2^3) / (t2 t4 - t3^2) <= rank(M).
    """
    m = len(gram_psd)
    M1 = [[require_exact_rational(x, "entry") for x in row] for row in gram_psd]
    M2 = mat_mul_frac(M1, M1)
    M3 = mat_mul_frac(M2, M1)
    M4 = mat_mul_frac(M2, M2)
    t1 = sum((M1[i][i] for i in range(m)), Fraction(0))
    t2 = sum((M2[i][i] for i in range(m)), Fraction(0))
    t3 = sum((M3[i][i] for i in range(m)), Fraction(0))
    t4 = sum((M4[i][i] for i in range(m)), Fraction(0))
    r_opt = (t1 * t1) / t2 if t2 > 0 else Fraction(0)
    det2 = t2 * t4 - t3 * t3
    if det2 > 0:
        r_h4 = (t1 * t1 * t4 - 2 * t1 * t2 * t3 + t2 * t2 * t2) / det2
    else:
        r_h4 = r_opt
    if r_h4 < r_opt:
        raise RuntimeError("Monotonicity violation: R_H4 < R_opt on PSD matrix")
    return {
        "r_opt": r_opt,
        "r_opt_str": frac_str(r_opt),
        "r_opt_ceil": ceil_fraction(r_opt),
        "r_h4": r_h4,
        "r_h4_str": frac_str(r_h4),
        "r_h4_ceil": ceil_fraction(r_h4),
        "r_opt_x10000": int((r_opt * 10000).numerator // (r_opt * 10000).denominator),
        "r_h4_x10000": int((r_h4 * 10000).numerator // (r_h4 * 10000).denominator),
    }


def euler_witt_and_log_deriv(seq: list[int], max_n: int) -> tuple[list[Fraction], list[Fraction]]:
    """Exact logarithmic derivative c_n = [q^n] q A'(q)/A(q) and Mobius-inverted
    Euler-Witt exponents b_n where A(q)/a_0 = prod_{k>=1} (1 - q^k)^{-b_k}.
    """
    if not seq or seq[0] == 0:
        raise ValueError("Series must have nonzero constant term a_0 for Euler-Witt transform")
    max_int = require_exact_int(max_n, "max_n")
    if max_int < 1 or max_int >= len(seq):
        raise ValueError("max_n out of range for input series")
    a0 = require_exact_int(seq[0], "a_0")
    an = [Fraction(require_exact_int(seq[i], f"seq[{i}]"), a0) for i in range(max_int + 1)]
    c = [Fraction(0)] * (max_int + 1)
    for n in range(1, max_int + 1):
        acc = n * an[n]
        for k in range(1, n):
            if c[k] and an[n - k]:
                acc -= c[k] * an[n - k]
        c[n] = acc
    b = [Fraction(0)] * (max_int + 1)
    for n in range(1, max_int + 1):
        acc = c[n]
        for d in range(1, n):
            if n % d == 0:
                acc -= d * b[d]
        b[n] = acc / n
    return b[1:], c[1:]


def hankel_matrix(seq: list[int | Fraction], m: int, shift: int = 0) -> list[list[Fraction]]:
    m_int = require_exact_int(m, "m")
    sh = require_exact_int(shift, "shift")
    if m_int < 1 or sh < 0 or sh + 2 * m_int - 1 >= len(seq):
        raise ValueError("Hankel dimensions exceed sequence length")
    return [[require_exact_rational(seq[i + j + sh], "h") for j in range(m_int)] for i in range(m_int)]


def run_four_tier_filtration(lib: dict[str, list[int]], n_terms: int) -> dict[str, Any]:
    """Execute the complete 4-tier coordinate-free exact matrix-minor filtration
    plus Law-3 additive-Hankel refutation and CS-11 null-shuffled controls.
    """
    # --- Law-3 Refutation Witness ---
    # 1) theta3(q) = 2 * partial_theta(q) - 1 -> H_m^{(1)}(theta3) == 2 * H_m^{(1)}(partial_theta) identically!
    h1_th3 = hankel_matrix(lib["theta3"], 12, shift=1)
    h1_pt = hankel_matrix(lib["partial_theta"], 12, shift=1)
    shifted_hankel_exact_ratio_2 = all(
        h1_th3[i][j] == 2 * h1_pt[i][j] for i in range(12) for j in range(12)
    )
    if not shifted_hankel_exact_ratio_2:
        raise RuntimeError("Law-3 witness theta3 vs partial_theta shifted Hankel failed")

    # 2) Partition p(n) Turan log-concavity witness: det H_2^{(s)}(p) = p(s)p(s+2) - p(s+1)^2 < 0 for all s in 25..65
    p_ser = lib["p_ser"]
    turan_neg_all = all(p_ser[s] * p_ser[s + 2] - p_ser[s + 1] ** 2 < 0 for s in range(25, n_terms - 2))
    if not turan_neg_all:
        raise RuntimeError("Partition Turan 2x2 Hankel negativity check failed")

    # --- Tier 1 & Tier 2: Additive Hankel H_10(A) vs Euler-Witt Hankel H_10(b(A)) ---
    rng = random.Random(20261121)

    def make_shuffled(seq: list[int]) -> list[int]:
        head_win = seq[1:45]
        rng.shuffle(head_win)
        return [seq[0]] + head_win + seq[45:]

    # Shadow-cancelling vs shadow-doubling combinations (Order 3 & Order 5)
    m3_cancel_f_psi = q_add(lib["m3_f"], q_scale(4, q_neg(lib["m3_psi"], n_terms), n_terms), n_terms)
    m3_double_f_psi = q_sub(lib["m3_f"], q_scale(4, q_neg(lib["m3_psi"], n_terms), n_terms), n_terms)
    m3_cancel_chi_f = q_sub(q_scale(4, lib["m3_chi"], n_terms), lib["m3_f"], n_terms)
    m3_cancel_rho_om = q_add(q_scale(2, lib["m3_rho"], n_terms), lib["m3_omega"], n_terms)
    q_om_q2 = q_shift(q_sub_pow(lib["m3_omega"], 2, n_terms), 1, n_terms)
    m3_cancel_nu_om = q_add(lib["m3_nu"], q_om_q2, n_terms)
    m3_double_nu_om = q_sub(lib["m3_nu"], q_om_q2, n_terms)

    m5_cancel_f0_psi0 = q_add(lib["m5_f0"], q_scale(2, q_neg(lib["m5_psi0"], n_terms), n_terms), n_terms)
    m5_cancel_psi1_f1 = q_sub(q_scale(2, q_neg(lib["m5_psi1"], n_terms), n_terms), lib["m5_f1"], n_terms)
    phi0_neg_q2 = [0] * n_terms
    for i in range(n_terms):
        if 2 * i < n_terms:
            phi0_neg_q2[2 * i] = lib["m5_phi0"][i] if (i & 1) == 0 else -lib["m5_phi0"][i]
    m5_cancel_phi0_psi0 = q_add(phi0_neg_q2, lib["m5_psi0"], n_terms)
    m5_double_phi0_psi0 = q_sub(phi0_neg_q2, lib["m5_psi0"], n_terms)

    # CS-11 null-shuffled controls (seeded deterministically)
    shuf_eta1 = make_shuffled(lib["eta1"])
    shuf_theta3 = make_shuffled(lib["theta3"])
    shuf_crank = make_shuffled(lib["crank_neg1"])
    shuf_m3_f = make_shuffled(lib["m3_f"])

    # Also test period-20 collapse at m=14 (requires 27 Euler exponents)
    panel = [
        ("rational_fib", "rational", lib["rational_fib"]),
        ("eta1", "modular_eta_quot", lib["eta1"]),
        ("p_ser_1_over_eta", "modular_eta_quot", lib["p_ser"]),
        ("delta_q_tau", "modular_eta_quot", lib["delta_q"]),
        ("theta3", "modular_eta_quot", lib["theta3"]),
        ("theta4", "modular_eta_quot", lib["theta4"]),
        ("crank_neg1", "modular_eta_quot", lib["crank_neg1"]),
        ("E4", "modular_interior_zero", lib["E4"]),
        ("E6", "modular_interior_zero", lib["E6"]),
        ("E2", "quasimodular", lib["E2"]),
        ("m3_f", "mock_order3", lib["m3_f"]),
        ("m3_phi", "mock_order3", lib["m3_phi"]),
        ("m3_chi", "mock_order3", lib["m3_chi"]),
        ("m3_omega", "mock_order3", lib["m3_omega"]),
        ("m3_nu", "mock_order3", lib["m3_nu"]),
        ("m3_rho", "mock_order3", lib["m3_rho"]),
        ("m5_f0", "mock_order5", lib["m5_f0"]),
        ("m5_F0", "mock_order5", lib["m5_F0"]),
        ("m7_F0", "mock_order7", lib["m7_F0"]),
        ("partial_theta", "partial_theta", lib["partial_theta"]),
        ("false_tri", "false_theta", lib["false_tri"]),
        ("false_pent", "false_theta", lib["false_pent"]),
        ("m3_cancel_f_plus_4psi_neg", "mock_shadow_cancelled", m3_cancel_f_psi),
        ("m3_double_f_minus_4psi_neg", "mock_shadow_doubled", m3_double_f_psi),
        ("m3_cancel_4chi_minus_f", "mock_shadow_cancelled", m3_cancel_chi_f),
        ("m3_cancel_2rho_plus_omega", "mock_shadow_cancelled", m3_cancel_rho_om),
        ("m3_cancel_nu_plus_q_om_q2", "mock_shadow_cancelled", m3_cancel_nu_om),
        ("m3_double_nu_minus_q_om_q2", "mock_shadow_doubled", m3_double_nu_om),
        ("m5_cancel_f0_plus_2psi0_neg", "mock_shadow_cancelled", m5_cancel_f0_psi0),
        ("m5_cancel_2psi1_neg_minus_f1", "mock_shadow_cancelled", m5_cancel_psi1_f1),
        ("m5_cancel_phi0_neg_q2_plus_psi0", "mock_shadow_cancelled", m5_cancel_phi0_psi0),
        ("m5_double_phi0_neg_q2_minus_psi0", "mock_shadow_doubled", m5_double_phi0_psi0),
        ("cs11_shuf_eta1", "cs11_null_shuffled", shuf_eta1),
        ("cs11_shuf_theta3", "cs11_null_shuffled", shuf_theta3),
        ("cs11_shuf_crank_neg1", "cs11_null_shuffled", shuf_crank),
        ("cs11_shuf_m3_f", "cs11_null_shuffled", shuf_m3_f),
    ]

    m_add = 12
    m_low = 10
    m_high = 14
    tier12_rows: list[dict[str, Any]] = []
    for name, cls, seq in panel:
        h_a = hankel_matrix(seq, m_add, shift=0)
        in_a = exact_symmetric_inertia(h_a)
        b_long, _ = euler_witt_and_log_deriv(seq, 42)
        in_b10 = exact_symmetric_inertia(hankel_matrix(b_long, m_low, shift=0))
        in_b14 = exact_symmetric_inertia(hankel_matrix(b_long, m_high, shift=0))
        rank_a = in_a[0] + in_a[2]
        rank_b10 = in_b10[0] + in_b10[2]
        rank_b14 = in_b14[0] + in_b14[2]
        detected_period = None
        for per in range(1, 21):
            if all(b_long[i] == b_long[i + per] for i in range(len(b_long) - per)):
                detected_period = per
                break
        tier12_rows.append({
            "name": name,
            "class": cls,
            "additive_H12_inertia": list(in_a),
            "additive_H12_rank": rank_a,
            "euler_witt_H10_rank": rank_b10,
            "euler_witt_H14_inertia": list(in_b14),
            "euler_witt_H14_rank": rank_b14,
            "euler_witt_saturated_by_14": rank_b14 == rank_b10 and rank_b14 < m_low,
            "euler_witt_exact_period_up_to_42": detected_period,
            "b_first_10": [frac_str(x) for x in b_long[:10]],
        })

    # Verify strict Tier-2 theorems programmatically (rank saturation vs strict growth 10 -> 14)
    row_by_name = {r["name"]: r for r in tier12_rows}
    if row_by_name["rational_fib"]["additive_H12_rank"] != 2:
        raise RuntimeError("Kronecker rational Fibonacci Hankel rank != 2")
    for eta_nm, exp_rk in [
        ("eta1", 1),
        ("p_ser_1_over_eta", 1),
        ("delta_q_tau", 1),
        ("theta4", 2),
        ("crank_neg1", 2),
        ("theta3", 3),
        ("m3_cancel_f_plus_4psi_neg", 2),
        ("m3_cancel_nu_plus_q_om_q2", 4),
        ("m3_cancel_2rho_plus_omega", 4),
        ("m3_cancel_4chi_minus_f", 5),
        ("m5_cancel_f0_plus_2psi0_neg", 6),
        ("m5_cancel_2psi1_neg_minus_f1", 6),
    ]:
        r_row = row_by_name[eta_nm]
        if not (r_row["euler_witt_H10_rank"] == exp_rk and r_row["euler_witt_H14_rank"] == exp_rk):
            raise RuntimeError(f"Expected saturated Euler-Witt rank {exp_rk} for {eta_nm}, got ({r_row['euler_witt_H10_rank']}, {r_row['euler_witt_H14_rank']})")
    # Dedicated m=22 check for period-20 5th-order shadow cancellation vs wrong-sign shadow doubling
    b_p20_cancel, _ = euler_witt_and_log_deriv(m5_cancel_phi0_psi0, 46)
    b_p20_double, _ = euler_witt_and_log_deriv(m5_double_phi0_psi0, 46)
    in_p20_cancel = exact_symmetric_inertia(hankel_matrix(b_p20_cancel, 22, 0))
    in_p20_double = exact_symmetric_inertia(hankel_matrix(b_p20_double, 22, 0))
    rk_p20_cancel = in_p20_cancel[0] + in_p20_cancel[2]
    rk_p20_double = in_p20_double[0] + in_p20_double[2]
    if not (rk_p20_cancel < 22 and rk_p20_double == 22):
        raise RuntimeError(f"Period-20 m=22 collapse check failed: cancel={rk_p20_cancel}, double={rk_p20_double}")
    for full_nm in [
        "m3_f",
        "m3_phi",
        "m3_chi",
        "m3_omega",
        "m3_nu",
        "m3_rho",
        "m5_f0",
        "m5_F0",
        "m7_F0",
        "partial_theta",
        "false_tri",
        "false_pent",
        "m3_double_f_minus_4psi_neg",
        "m3_double_nu_minus_q_om_q2",
        "m5_double_phi0_neg_q2_minus_psi0",
    ]:
        r_row = row_by_name[full_nm]
        if not (r_row["euler_witt_H10_rank"] == m_low and r_row["euler_witt_H14_rank"] == m_high):
            raise RuntimeError(f"Expected non-saturating Euler-Witt rank ({m_low}->{m_high}) for {full_nm}, got ({r_row['euler_witt_H10_rank']}, {r_row['euler_witt_H14_rank']})")
    for shuf_nm, base_nm in [
        ("cs11_shuf_eta1", "eta1"),
        ("cs11_shuf_theta3", "theta3"),
        ("cs11_shuf_crank_neg1", "crank_neg1"),
        ("cs11_shuf_m3_f", "m3_f"),
    ]:
        s_row = row_by_name[shuf_nm]
        b_row = row_by_name[base_nm]
        if not (
            s_row["euler_witt_H14_rank"] > s_row["euler_witt_H10_rank"]
            and s_row["euler_witt_exact_period_up_to_42"] is None
            and (base_nm == "m3_f" or s_row["euler_witt_H14_rank"] > b_row["euler_witt_H14_rank"])
        ):
            raise RuntimeError(f"CS-11 shuffled control {shuf_nm} failed non-saturation check: {s_row}")

    # --- Tier 3: Log-derivative H_8(c)^2 R_opt vs R_H4 + Ramanujan ODE + Hecke Schur Closure ---
    tier3_r_opt_rh4: list[dict[str, Any]] = []
    for name, cls in [
        ("E4", "modular_interior_zero"),
        ("E6", "modular_interior_zero"),
        ("E2", "quasimodular"),
        ("m3_f", "mock_order3"),
        ("m5_f0", "mock_order5"),
        ("false_pent", "false_theta"),
        ("partial_theta", "partial_theta"),
    ]:
        _, c_seq = euler_witt_and_log_deriv(lib[name], 20)
        h_c = hankel_matrix(c_seq, 8, shift=0)
        gram_c = mat_mul_frac(h_c, h_c)
        bounds = psd_r_opt_and_r_h4(gram_c)
        tier3_r_opt_rh4.append({
            "name": name,
            "class": cls,
            "r_opt_ceil": bounds["r_opt_ceil"],
            "r_h4_ceil": bounds["r_h4_ceil"],
            "r_opt_x10000": bounds["r_opt_x10000"],
            "r_h4_x10000": bounds["r_h4_x10000"],
            "r_opt_num_bits": bounds["r_opt"].numerator.bit_length(),
            "r_h4_num_bits": bounds["r_h4"].numerator.bit_length(),
        })

    # Verify strict R_H4 separation: E4/E6/E2 have r_h4_ceil <= 3 while m3_f >= 4, false_pent >= 5, partial_theta >= 6
    t3_map = {r["name"]: r for r in tier3_r_opt_rh4}
    if not (
        t3_map["E4"]["r_h4_ceil"] <= 3
        and t3_map["E6"]["r_h4_ceil"] <= 3
        and t3_map["E2"]["r_h4_ceil"] <= 3
        and t3_map["m3_f"]["r_h4_ceil"] >= 4
        and t3_map["false_pent"]["r_h4_ceil"] >= 5
        and t3_map["partial_theta"]["r_h4_ceil"] >= 6
    ):
        raise RuntimeError(f"Tier-3 R_H4 separation failed: {tier3_r_opt_rh4}")

    # Ramanujan 1916 ODE system: 12 D(E2) = E2^2 - E4, 3 D(E4) = E2 E4 - E6, 2 D(E6) = E2 E6 - E4^2
    e2, e4, e6 = lib["E2"], lib["E4"], lib["E6"]
    ode_1 = q_scale(12, q_theta_deriv(e2, n_terms), n_terms) == q_sub(q_mul(e2, e2, n_terms), e4, n_terms)
    ode_2 = q_scale(3, q_theta_deriv(e4, n_terms), n_terms) == q_sub(q_mul(e2, e4, n_terms), e6, n_terms)
    ode_3 = q_scale(2, q_theta_deriv(e6, n_terms), n_terms) == q_sub(q_mul(e2, e6, n_terms), q_mul(e4, e4, n_terms), n_terms)
    if not (ode_1 and ode_2 and ode_3):
        raise RuntimeError("Ramanujan 1916 ODE closure failed")

    # Exact Hecke-Gram Schur complement S(Delta, T_{p,12} Delta) == 0 for p in {2, 3, 5}
    # Compute tau[1..65] from delta_q[0..64]
    tau_short = [0] + lib["delta_q"][: n_terms - 1]
    hecke_schur_zero: dict[str, bool] = {}
    for p in (2, 3, 5):
        m_chk = (n_terms - 1) // p
        v_delta = [Fraction(tau_short[n]) for n in range(1, m_chk + 1)]
        v_tp = []
        for n in range(1, m_chk + 1):
            val = tau_short[p * n]
            if n % p == 0:
                val += (p ** 11) * tau_short[n // p]
            v_tp.append(Fraction(val))
        g11 = sum((x * x for x in v_delta), Fraction(0))
        g12 = sum((x * y for x, y in zip(v_delta, v_tp)), Fraction(0))
        g22 = sum((y * y for y in v_tp), Fraction(0))
        schur = g22 - (g12 * g12) / g11
        if schur != 0:
            raise RuntimeError(f"Hecke Schur complement nonzero for p={p}: {schur}")
        hecke_schur_zero[f"p={p}"] = True

    return {
        "law3_additive_hankel_refutation": {
            "theta3_vs_partial_theta_shifted_H12_exact_ratio_2": shifted_hankel_exact_ratio_2,
            "partition_turan_2x2_hankel_det_negative_for_s_25_to_67": turan_neg_all,
            "conclusion": "Additive Hankel inertia alone CANNOT separate modular from partial/mock thetas.",
        },
        "tier1_and_tier2_hankel_table": tier12_rows,
        "tier2_period20_m22_collapse": {
            "hankel_size": 22,
            "cancel_phi0_neg_q2_plus_psi0_rank": rk_p20_cancel,
            "cancel_phi0_neg_q2_plus_psi0_inertia": list(in_p20_cancel),
            "double_phi0_neg_q2_minus_psi0_rank": rk_p20_double,
            "double_phi0_neg_q2_minus_psi0_inertia": list(in_p20_double),
        },
        "tier3_log_deriv_r_opt_vs_r_h4": tier3_r_opt_rh4,
        "tier3_ramanujan_ode_closure_order": n_terms,
        "tier3_ramanujan_ode_all_exact_zero_residual": True,
        "tier3_hecke_gram_schur_zero": hecke_schur_zero,
    }


# ============================================================================
# Part 3: Exact Dyson Rank vs Andrews-Garvan Crank p-Dissection
#         Column-Space Schur Complement S_shadow(p, r) (p in {5, 7, 11, 13})
# ============================================================================

def compute_rank_crank_mod_p(n_terms: int, p: int) -> tuple[list[list[int]], list[list[int]]]:
    """Exact bivariate Z[z]/(z^p - 1)[[q]] mod q^{n_terms} for Dyson rank R(z;q)
    and Andrews-Garvan crank C(z;q).
    Note: for n >= 2, C(z;q) matches Garvan's combinatorial crank M(m, n) identically
    (at n=1, C(z;q) gives z - 1 + z^{-1}; combinatorial crank of (1) is 0).
    """
    p_int = require_exact_int(p, "p")
    n_int = require_exact_int(n_terms, "n_terms")
    if p_int < 3 or n_int < 2:
        raise ValueError("compute_rank_crank_mod_p requires p >= 3 and n_terms >= 2")

    def mul_factor(s: list[list[int]], pow_a: int, z_shift: int) -> list[list[int]]:
        if pow_a >= n_int:
            return [row[:] for row in s]
        out = [row[:] for row in s]
        for n in range(n_int - 1, pow_a - 1, -1):
            prev = out[n - pow_a]
            cur = out[n]
            for r in range(p_int):
                cur[r] -= prev[(r - z_shift) % p_int]
        return out

    def mul_factor_inv(s: list[list[int]], pow_a: int, z_shift: int) -> list[list[int]]:
        if pow_a >= n_int:
            return [row[:] for row in s]
        out = [row[:] for row in s]
        for n in range(pow_a, n_int):
            prev = out[n - pow_a]
            cur = out[n]
            for r in range(p_int):
                cur[r] += prev[(r - z_shift) % p_int]
        return out

    C = [[0] * p_int for _ in range(n_int)]
    C[0][0] = 1
    for k in range(1, n_int):
        C = mul_factor(C, k, 0)
    for k in range(1, n_int):
        C = mul_factor_inv(C, k, 1)
        C = mul_factor_inv(C, k, p_int - 1)

    R = [[0] * p_int for _ in range(n_int)]
    term = [[0] * p_int for _ in range(n_int)]
    term[0][0] = 1
    R[0][0] = 1
    m = 1
    while m * m < n_int:
        term = mul_factor_inv(term, m, 1)
        term = mul_factor_inv(term, m, p_int - 1)
        e = m * m
        for n in range(n_int - e):
            for r in range(p_int):
                R[n + e][r] += term[n][r]
        m += 1
    return R, C


def legendre_symbol(a: int, p: int) -> int:
    r = pow(a % p, (p - 1) // 2, p)
    if r == 0:
        return 0
    return -1 if r == p - 1 else 1


def run_rank_crank_schur_obstruction(lib: dict[str, list[int]]) -> dict[str, Any]:
    """Compute exact Column-Space Schur Complement S_shadow(p, r) = B^T B - B^T A (A^T A)^+ A^T B
    across all residue classes for p in {5, 7, 11, 13}, verify the exact Legendre selection
    law on p in {5, 7}, all 3 Hickerson 7th-order mock theta identities, the genus-1
    rank-5 explosion on p=11 (with Bareiss PD, R_opt, R_H4, and O(5, Q) invariance),
    and Garvan rank-1 termination at p=13.
    """
    prime_configs = [(5, 95, 4), (7, 160, 5), (11, 150, 6), (13, 180, None)]
    by_prime: dict[str, Any] = {}
    hickerson_7th_checks: dict[str, bool] = {}
    mod11_class6_cert: dict[str, Any] = {}

    for p, n_lim, delta_cong in prime_configs:
        R, C = compute_rank_crank_mod_p(n_lim, p)
        h = (p - 1) // 2

        # Verify total sum == p(n) and Ramanujan congruence if applicable
        congruence_defects: list[dict[str, int]] = []
        if delta_cong is not None:
            for n in range(delta_cong, n_lim, p):
                pn = sum(R[n])
                if pn != sum(C[n]):
                    raise RuntimeError(f"Partition sum mismatch at p={p}, n={n}")
                if pn % p != 0:
                    raise RuntimeError(f"Ramanujan congruence failed at p={p}, n={n}")
                d_rank = p * sum(x * x for x in R[n]) - pn * pn
                d_crank = p * sum(x * x for x in C[n]) - pn * pn
                if d_crank != 0:
                    raise RuntimeError(f"Crank failed equidistribution at p={p}, n={n}")
                if p in (5, 7) and d_rank != 0:
                    raise RuntimeError(f"Rank failed equidistribution at p={p}, n={n}")
                if p == 11 and d_rank <= 0:
                    raise RuntimeError(f"Expected strictly positive rank defect at 11k+6, n={n}")
                congruence_defects.append({
                    "n": n,
                    "p_n": pn,
                    "parseval_defect_rank": d_rank,
                    "parseval_defect_crank": d_crank,
                })

        crank_ranks: list[int] = []
        rank_ranks: list[int] = []
        shadow_schur_ranks: list[int] = []
        legendre_1_minus_24r: list[int] = []

        for rem in range(p):
            A_int = [[C[n][b] - C[n][0] for b in range(1, h + 1)] for n in range(rem, n_lim, p) if n >= 2]
            B_int = [[R[n][b] - R[n][0] for b in range(1, h + 1)] for n in range(rem, n_lim, p) if n >= 2]
            A = [[Fraction(x) for x in row] for row in A_int]
            B = [[Fraction(x) for x in row] for row in B_int]
            AT = mat_transpose_frac(A)
            BT = mat_transpose_frac(B)
            G_AA = mat_mul_frac(AT, A)
            G_AB = mat_mul_frac(AT, B)
            G_BA = mat_mul_frac(BT, A)
            G_BB = mat_mul_frac(BT, B)
            G_AA_pinv = exact_pinv_symmetric_psd(G_AA)
            corr = mat_mul_frac(mat_mul_frac(G_BA, G_AA_pinv), G_AB)
            S_shadow = [[G_BB[i][j] - corr[i][j] for j in range(h)] for i in range(h)]
            in_s = exact_symmetric_inertia(S_shadow)
            if in_s[2] != 0:
                raise RuntimeError(f"Negative eigenvalue in PSD Schur complement S_shadow({p},{rem})")
            rk_a = exact_col_rank(A)
            rk_b = exact_col_rank(B)
            rk_ab = exact_col_rank([a + b for a, b in zip(A, B)])
            rk_s = in_s[0]
            # Verify exact Haynsworth-Schur rank additivity: rank(S_shadow) == rank([A|B]) - rank(A)
            if rk_s != rk_ab - rk_a:
                raise RuntimeError(f"Schur rank additivity failed at p={p}, rem={rem}: {rk_s} != {rk_ab - rk_a}")

            crank_ranks.append(rk_a)
            rank_ranks.append(rk_b)
            shadow_schur_ranks.append(rk_s)
            legendre_1_minus_24r.append(legendre_symbol(1 - 24 * rem, p))

            if p == 11 and rem == 6:
                minors = exact_bareiss_leading_minors(S_shadow)
                if not all(m_val > 0 for m_val in minors):
                    raise RuntimeError("S_shadow(11, 6) is not strictly positive definite!")
                spec = psd_r_opt_and_r_h4(S_shadow)
                if spec["r_opt"] <= 1 or spec["r_h4"] <= 1:
                    raise RuntimeError("Expected R_opt > 1 and R_H4 > 1 on S_shadow(11, 6)")

                # Exact O(5, Q) Householder orthogonal invariance test: H = I - 2 u u^T / (u^T u)
                u_vec = [Fraction(1), Fraction(-2), Fraction(3), Fraction(-1), Fraction(2)]
                uu = sum((x * x for x in u_vec), Fraction(0))
                Q_orth = [
                    [Fraction(1 if i == j else 0) - Fraction(2) * u_vec[i] * u_vec[j] / uu for j in range(5)]
                    for i in range(5)
                ]
                S_rot = mat_mul_frac(mat_mul_frac(Q_orth, S_shadow), Q_orth)
                spec_rot = psd_r_opt_and_r_h4(S_rot)
                in_rot = exact_symmetric_inertia(S_rot)
                if spec_rot["r_opt"] != spec["r_opt"] or spec_rot["r_h4"] != spec["r_h4"] or in_rot != in_s:
                    raise RuntimeError("O(5, Q) orthogonal invariance failed on S_shadow(11, 6)")

                mod11_class6_cert = {
                    "matrix_dim": 5,
                    "inertia": list(in_s),
                    "strictly_positive_definite": True,
                    "leading_principal_minors_all_positive": True,
                    "leading_minor_bit_lengths": [m_val.numerator.bit_length() for m_val in minors],
                    "r_opt_str": spec["r_opt_str"],
                    "r_opt_ceil": spec["r_opt_ceil"],
                    "r_opt_x10000": spec["r_opt_x10000"],
                    "r_h4_str": spec["r_h4_str"],
                    "r_h4_ceil": spec["r_h4_ceil"],
                    "r_h4_x10000": spec["r_h4_x10000"],
                    "O5Q_householder_zero_residual_invariant": True,
                    "S_shadow_matrix_int": [[int(S_shadow[i][j]) for j in range(5)] for i in range(5)],
                }

        # Verify exact Legendre selection law for p in {5, 7}
        legendre_law_exact = all(
            shadow_schur_ranks[r] == (1 if legendre_1_minus_24r[r] == 1 else 0)
            for r in range(p)
        )
        if p in (5, 7) and not legendre_law_exact:
            raise RuntimeError(f"Legendre selection law failed at p={p}")
        if p == 11 and not (
            crank_ranks == [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1]
            and shadow_schur_ranks == [5] * 11
        ):
            raise RuntimeError(f"Mod-11 genus-1 phase transition mismatch: {crank_ranks} / {shadow_schur_ranks}")
        if p == 13 and not (crank_ranks == [6] * 13 and shadow_schur_ranks == [6] * 13):
            raise RuntimeError(f"Mod-13 Garvan termination mismatch: {crank_ranks} / {shadow_schur_ranks}")

        # Verify all 3 Hickerson (1988) 7th-order mock theta rank-difference identities on QR classes {0, 2, 6}
        if p == 7:
            k_chk = 22
            f0_7 = lib["m7_F0"][:k_chk]
            f1_7 = lib["m7_F1"][1 : k_chk + 1]
            f2_7 = lib["m7_F2"][:k_chk]
            chk_f0 = [R[7 * k][0] - R[7 * k][2] for k in range(k_chk)] == f0_7
            chk_f2 = [R[7 * k + 2][1] - R[7 * k + 2][2] for k in range(k_chk)] == f2_7
            chk_f1 = [2 * R[7 * k + 6][2] - R[7 * k + 6][1] - R[7 * k + 6][0] for k in range(k_chk)] == f1_7
            hickerson_7th_checks = {
                "terms_verified": k_chk,
                "7k_plus_0_N0_minus_N2_eq_F0": chk_f0,
                "7k_plus_2_N1_minus_N2_eq_F2": chk_f2,
                "7k_plus_6_2N2_minus_N1_minus_N0_eq_qinv_F1": chk_f1,
            }
            if not (chk_f0 and chk_f2 and chk_f1):
                raise RuntimeError(f"Hickerson 7th-order identity failed: {hickerson_7th_checks}")

        by_prime[f"p={p}"] = {
            "prime": p,
            "palindromic_dim": h,
            "n_limit": n_lim,
            "congruence_class": delta_cong,
            "crank_ranks_by_rem": crank_ranks,
            "rank_ranks_by_rem": rank_ranks,
            "S_shadow_ranks_by_rem": shadow_schur_ranks,
            "legendre_1_minus_24r": legendre_1_minus_24r,
            "legendre_selection_law_exact": legendre_law_exact,
            "congruence_parseval_defects_first_8": congruence_defects[:8],
            "congruence_terms_checked": len(congruence_defects),
        }

    return {
        "by_prime": by_prime,
        "hickerson_7th_order_mock_theta_identities": hickerson_7th_checks,
        "mod11_class6_shadow_certificate": mod11_class6_cert,
    }


# ============================================================================
# Part 4: Exact BigInt Ramanujan tau(n) (n=1..500), Cubic Theta AGM (O(q^100)),
#         and Commit-Pinned 3-Lab aletheia v1.2.0 --lean-audit Forensics
# ============================================================================

def compute_tau_table(m_max: int = 500) -> list[int]:
    """Compute exact Ramanujan tau(n) for n=1..m_max via Euler pentagonal^24."""
    m_int = require_exact_int(m_max, "m_max")
    if m_int < 10:
        raise ValueError("m_max must be >= 10")
    pent = [0] * m_int
    k = 0
    while True:
        e1 = k * (3 * k - 1) // 2
        e2 = k * (3 * k + 1) // 2
        if e1 >= m_int and e2 >= m_int:
            break
        s = 1 if (k & 1) == 0 else -1
        if e1 < m_int:
            pent[e1] = s
        if k > 0 and e2 < m_int:
            pent[e2] = s
        k += 1
    p2 = q_mul(pent, pent, m_int)
    p4 = q_mul(p2, p2, m_int)
    p8 = q_mul(p4, p4, m_int)
    p16 = q_mul(p8, p8, m_int)
    p24 = q_mul(p16, p8, m_int)
    return [0] + p24


def sigma_mod(n: int, k: int, mod: int) -> int:
    total = 0
    lim = math.isqrt(n)
    for d in range(1, lim + 1):
        if n % d == 0:
            total = (total + pow(d, k, mod)) % mod
            q = n // d
            if q != d:
                total = (total + pow(q, k, mod)) % mod
    return total


def run_tau_and_cubic_agm(m_tau: int = 500, n_agm: int = 100) -> dict[str, Any]:
    """Exact BigInt verification of Ramanujan tau(n) congruences, Hecke
    multiplicativity & prime-power recursion, integer Deligne bound, Lehmer
    non-vanishing, plus Borwein-Ramanujan cubic theta AGM a(q)^3 = b(q)^3 + c(q)^3.
    """
    tau = compute_tau_table(m_tau)
    primes = [
        p for p in range(2, m_tau + 1)
        if all(p % d != 0 for d in range(2, math.isqrt(p) + 1))
    ]

    # 1. Classical Ramanujan-Wilton-Kolberg-Swinnerton-Dyer congruences
    c_691 = all((tau[n] - sigma_mod(n, 11, 691)) % 691 == 0 for n in range(1, m_tau + 1))
    kol2 = {1: 1, 3: 1217, 5: 1537, 7: 705}
    c_2048_odd = all(
        (tau[n] - kol2[n & 7] * sigma_mod(n, 11, 2048)) % 2048 == 0
        for n in range(1, m_tau + 1, 2)
    )
    c_729_c3 = all(
        (tau[n] - pow(n, 135, 729) * sigma_mod(n, 227, 729)) % 729 == 0
        for n in range(1, m_tau + 1)
        if n % 3 != 0
    )
    c_125_c5 = all(
        (tau[n] - pow(n, 41, 125) * sigma_mod(n, 29, 125)) % 125 == 0
        for n in range(1, m_tau + 1)
        if n % 5 != 0
    )
    c_7 = all((tau[n] - n * sigma_mod(n, 3, 7)) % 7 == 0 for n in range(1, m_tau + 1))
    c_23_inert = all(tau[p] % 23 == 0 for p in primes if p != 23 and legendre_symbol(p, 23) == -1)
    c_23_split = all((tau[p] % 23) in (2, 22) for p in primes if p != 23 and legendre_symbol(p, 23) == 1)

    # 2. Hecke multiplicativity & prime-power recurrence
    coprime_pairs = 0
    for m in range(1, m_tau + 1):
        for n in range(m, m_tau // m + 1):
            if math.gcd(m, n) == 1:
                if tau[m * n] != tau[m] * tau[n]:
                    raise RuntimeError(f"Hecke multiplicativity failed at ({m}, {n})")
                coprime_pairs += 1
    pp_checks = 0
    for p in primes:
        pr = p
        prev = 1
        while pr * p <= m_tau:
            nxt = pr * p
            if tau[nxt] != tau[p] * tau[pr] - (p ** 11) * tau[prev]:
                raise RuntimeError(f"Hecke prime-power recurrence failed at p={p}, p^(r+1)={nxt}")
            prev = pr
            pr = nxt
            pp_checks += 1

    # 3. Exact integer Deligne bound tau(p)^2 <= 4 * p^11 and Lehmer non-vanishing
    max_sato_tate_ratio = Fraction(0)
    max_sato_tate_prime = 2
    for p in primes:
        lhs = tau[p] * tau[p]
        rhs = 4 * (p ** 11)
        if lhs > rhs:
            raise RuntimeError(f"Deligne bound violated at p={p}")
        ratio = Fraction(lhs, rhs)
        if ratio > max_sato_tate_ratio:
            max_sato_tate_ratio = ratio
            max_sato_tate_prime = p

    lehmer_nonzero = all(tau[n] != 0 for n in range(1, m_tau + 1))
    if not (c_691 and c_2048_odd and c_729_c3 and c_125_c5 and c_7 and c_23_inert and c_23_split and lehmer_nonzero):
        raise RuntimeError("Ramanujan tau congruence or Lehmer check failed")

    # 4. Borwein-Ramanujan Cubic Theta AGM: a(q)^3 == b(q)^3 + c(q)^3 to O(q^{n_agm})
    lim = math.isqrt(2 * n_agm) + 2
    a_cub = [0] * n_agm
    b_cub_2x = [0] * n_agm
    c_tilde = [0] * n_agm
    for m in range(-lim, lim + 1):
        for n in range(-lim, lim + 1):
            e = m * m + m * n + n * n
            if e < n_agm:
                a_cub[e] += 1
                b_cub_2x[e] += 2 if (m - n) % 3 == 0 else -1
            ec = e + m + n
            if 0 <= ec < n_agm:
                c_tilde[ec] += 1
    if any((x & 1) != 0 for x in b_cub_2x):
        raise RuntimeError("b_cub_2x not even")
    b_cub_lat = [x // 2 for x in b_cub_2x]
    e1 = poch_inf(1, 1, 1, n_agm)
    e3 = poch_inf(1, 3, 3, n_agm)
    b_cub_prod = q_mul(q_pow(e1, 3, n_agm), q_inv_unit(e3, n_agm), n_agm)
    c3_prod_raw = q_mul(q_pow(e3, 9, n_agm), q_inv_unit(q_pow(e1, 3, n_agm), n_agm), n_agm)
    c3_prod = [0] + [27 * c3_prod_raw[i] for i in range(n_agm - 1)]
    c3_lat = [0] + q_pow(c_tilde, 3, n_agm - 1)
    a3 = q_pow(a_cub, 3, n_agm)
    b3 = q_pow(b_cub_lat, 3, n_agm)
    id_b_prod = b_cub_lat == b_cub_prod
    id_c3_prod = c3_lat == c3_prod
    id_cubic_pyth = a3 == q_add(b3, c3_prod, n_agm)
    a_q3 = q_sub_pow(a_cub, 3, n_agm)
    b_q3 = q_sub_pow(b_cub_lat, 3, n_agm)
    id_agm_1 = q_scale(3, a_q3, n_agm) == q_add(a_cub, q_scale(2, b_cub_lat, n_agm), n_agm)
    a2_ab_b2 = q_add(q_add(q_mul(a_cub, a_cub, n_agm), q_mul(a_cub, b_cub_lat, n_agm), n_agm), q_mul(b_cub_lat, b_cub_lat, n_agm), n_agm)
    id_agm_2 = q_scale(3, q_pow(b_q3, 3, n_agm), n_agm) == q_mul(b_cub_lat, a2_ab_b2, n_agm)
    # Check Euler-Witt Hankel rank of b(q) and c(q)/(3 q^{1/3}) = c_tilde/3
    b_ew_b, _ = euler_witt_and_log_deriv(b_cub_lat, 24)
    b_ew_c, _ = euler_witt_and_log_deriv(c_tilde, 24)
    rk_ew_b = sum(exact_symmetric_inertia(hankel_matrix(b_ew_b, 10, 0))[0::2])
    rk_ew_c = sum(exact_symmetric_inertia(hankel_matrix(b_ew_c, 10, 0))[0::2])
    if not (id_b_prod and id_c3_prod and id_cubic_pyth and id_agm_1 and id_agm_2 and rk_ew_b == 3 and rk_ew_c == 2):
        raise RuntimeError("Cubic theta AGM verification failed")

    return {
        "tau": {
            "range_n": [1, m_tau],
            "primes_checked": len(primes),
            "first_12": tau[1:13],
            "congruences": {
                "mod_691_sigma11_all_n": c_691,
                "mod_2048_kolberg_all_odd_n": c_2048_odd,
                "mod_729_swinnerton_dyer_coprime_3": c_729_c3,
                "mod_125_swinnerton_dyer_coprime_5": c_125_c5,
                "mod_7_n_sigma3_all_n": c_7,
                "mod_23_wilton_inert_primes_zero": c_23_inert,
                "mod_23_wilton_split_primes_in_2_or_minus1": c_23_split,
            },
            "hecke_coprime_pairs_verified": coprime_pairs,
            "hecke_prime_power_checks_verified": pp_checks,
            "deligne_integer_bound_all_primes": True,
            "max_sato_tate_ratio_prime": max_sato_tate_prime,
            "max_sato_tate_ratio_exact": frac_str(max_sato_tate_ratio),
            "max_sato_tate_ratio_x10000": int((max_sato_tate_ratio * 10000).numerator // (max_sato_tate_ratio * 10000).denominator),
            "lehmer_nonzero_all_n": lehmer_nonzero,
        },
        "cubic_theta_agm": {
            "truncation_order": n_agm,
            "b_lattice_eq_eta_product": id_b_prod,
            "c3_lattice_eq_eta_product": id_c3_prod,
            "a3_eq_b3_plus_c3": id_cubic_pyth,
            "agm_step1_3a_q3_eq_a_plus_2b": id_agm_1,
            "agm_step2_3b_q3_cubed_eq_b_a2_ab_b2": id_agm_2,
            "euler_witt_H10_rank_b": rk_ew_b,
            "euler_witt_H10_rank_c_tilde": rk_ew_c,
            "a_first_10": a_cub[:10],
            "b_first_10": b_cub_lat[:10],
            "c_tilde_first_10": c_tilde[:10],
        },
    }


def run_three_lab_lean4_audit(
    repos_root: Path | None = None,
    aletheia_root: Path | None = None,
) -> dict[str, Any]:
    """Run live aletheia v1.2.0 audit_lean4_source on 20 commit-pinned read-only
    Ramanujan Lean 4 files across Google DeepMind, OpenAI, and Anthropic when
    those external read-only clones and aletheia are present locally.
    In standalone clones of Foundation-0/ramanujan (where third-party repositories
    are not vendored), reports standalone mode cleanly without fabricating live results.
    """
    here = Path(__file__).resolve()
    if aletheia_root is None and len(here.parents) > 3:
        cand = here.parents[3] / "publish" / "aletheia"
        if (cand / "aletheia" / "audit_check.py").is_file():
            aletheia_root = cand
    if repos_root is None and len(here.parents) > 2:
        cand = here.parents[2] / "round3" / "repos"
        if cand.is_dir():
            repos_root = cand

    repo_names = ["dm-math-formal-conjectures", "openai-math", "anthropics-flt"]
    clones_ready = repos_root is not None and all(
        (repos_root / rn / ".git").exists() for rn in repo_names
    )
    if aletheia_root is None or not clones_ready:
        return {
            "mode": "standalone_no_external_clones",
            "note": (
                "External third-party Lean 4 repositories (dm-math-formal-conjectures@d8d031d4, "
                "openai-math@4eaee875, anthropics-flt@6e837e75) are not vendored in standalone "
                "Foundation-0/ramanujan; see certificates/ramanujan_mock_shadows_certificate.json "
                "for the sealed 20-file AUDIT-045 aletheia v1.2.0 forensics record."
            ),
            "total_lean_files_audited": 0,
        }

    if str(aletheia_root) not in sys.path:
        sys.path.insert(0, str(aletheia_root))
    import aletheia  # noqa: PLC0415
    from aletheia.audit_check import audit_lean4_source  # noqa: PLC0415

    repo_commits: dict[str, str] = {}
    for rn in repo_names:
        rdir = repos_root / rn
        proc = subprocess.run(
            ["git", "-C", str(rdir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_commits[rn] = proc.stdout.strip()

    pinned_rel_files = [
        "dm-math-formal-conjectures/FormalConjectures/Wikipedia/RamanujanTau.lean",
        "dm-math-formal-conjectures/FormalConjectures/Paper/PartitionParity.lean",
        "dm-math-formal-conjectures/FormalConjectures/Paper/Gourevitch.lean",
        "anthropics-flt/Theorems/Thm_EisensteinSeries_ramanujan_system_qExpansion_int.lean",
        "anthropics-flt/P2M/Sol/S_EisensteinSeries_ramanujan_system_qExpansion_int.lean",
    ]
    openai_ram = sorted(
        str(p.relative_to(repos_root)).replace("\\", "/")
        for p in (repos_root / "openai-math").rglob("*Ramanujan*.lean")
    )
    all_targets = pinned_rel_files + openai_ram

    per_file: list[dict[str, Any]] = []
    for rel in all_targets:
        fp = repos_root / rel
        src = fp.read_text(encoding="utf-8", errors="replace")
        r_strict = audit_lean4_source(src, allow_non_init_imports=False)
        r_mathlib = audit_lean4_source(src, allow_non_init_imports=True)
        sorry_lines = [f["line"] for f in r_mathlib["findings"] if f["code"] == "LEAN4_SORRY"]
        non_sorry_findings = [f for f in r_mathlib["findings"] if f["code"] != "LEAN4_SORRY"]
        non_init_imports = [
            {"line": f["line"], "module": f["excerpt"]}
            for f in r_strict["findings"]
            if f["code"] == "LEAN4_NON_INIT_IMPORT"
        ]
        per_file.append({
            "repo_file": rel,
            "sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
            "lines": src.count("\n") + 1,
            "has_public_import": "public import " in src,
            "mathlib_clean": r_mathlib["clean"],
            "sorry_count": len(sorry_lines),
            "sorry_lines": sorry_lines,
            "non_sorry_trust_escapes": non_sorry_findings,
            "non_init_import_count": len(non_init_imports),
        })

    dm_tau = next(x for x in per_file if x["repo_file"].endswith("RamanujanTau.lean"))
    if not (dm_tau["has_public_import"] and dm_tau["sorry_lines"] == [60, 66, 71]):
        raise RuntimeError(f"Unexpected RamanujanTau.lean audit profile: {dm_tau}")
    oai_clean_count = sum(1 for x in per_file if x["repo_file"].startswith("openai-math/") and x["mathlib_clean"])
    flt_clean_count = sum(1 for x in per_file if x["repo_file"].startswith("anthropics-flt/") and x["mathlib_clean"])
    if oai_clean_count != 15 or flt_clean_count != 2:
        raise RuntimeError(f"Unexpected openai/flt clean counts: {oai_clean_count}, {flt_clean_count}")

    return {
        "aletheia_version": aletheia.__version__,
        "pinned_repo_commits": repo_commits,
        "total_lean_files_audited": len(per_file),
        "openai_math_ramanujan_clean": f"{oai_clean_count}/15",
        "anthropics_flt_ramanujan_ode_clean": f"{flt_clean_count}/2",
        "dm_formal_conjectures_tau_public_import_and_tau2_sorry": True,
        "files": per_file,
    }


# ============================================================================
# Part 5: Built-in R3 Strict Domain / Type Negative Controls
# ============================================================================

def run_r3_negative_controls() -> dict[str, Any]:
    """Verify strict fail-closed rejection of invalid types/domains (zero silent fallbacks)."""
    controls: list[tuple[str, Any]] = [
        ("reject_float_in_exact_int", lambda: require_exact_int(1.0, "x")),
        ("reject_bool_in_exact_int", lambda: require_exact_int(True, "x")),
        ("reject_float_in_exact_rational", lambda: require_exact_rational(0.5, "x")),
        ("reject_bool_in_exact_rational", lambda: require_exact_rational(False, "x")),
        ("reject_zero_constant_q_inv", lambda: q_inv_unit([0, 1, 2], 3)),
        ("reject_nonunit_constant_q_inv", lambda: q_inv_unit([2, 1, 0], 3)),
        ("reject_zero_constant_euler_witt", lambda: euler_witt_and_log_deriv([0, 1, 2, 3], 2)),
        ("reject_asymmetric_matrix_inertia", lambda: exact_symmetric_inertia([[1, 2], [3, 4]])),
        ("reject_nonsquare_matrix_inertia", lambda: exact_symmetric_inertia([[1, 2, 3], [4, 5, 6]])),
        ("reject_invalid_modulus_rank_crank", lambda: compute_rank_crank_mod_p(10, 2)),
        ("reject_float_in_json_guard", lambda: verify_no_floats({"a": [1, 2.5]})),
    ]
    passed = 0
    details: dict[str, str] = {}
    for label, fn in controls:
        try:
            fn()
        except (TypeError, ValueError) as exc:
            passed += 1
            details[label] = f"REJECTED:{type(exc).__name__}"
        else:
            raise RuntimeError(f"R3 control failed to reject: {label}")
    return {
        "controls_passed": passed,
        "controls_total": len(controls),
        "all_rejected": passed == len(controls),
        "details": details,
    }


def run_all_probes(write_certificate: bool = False) -> dict[str, Any]:
    n_terms = 70
    lib = build_q_series_library(n_terms=n_terms)
    part1 = verify_mock_theta_and_appell_lerch_identities(lib, n_terms=n_terms)
    part2 = run_four_tier_filtration(lib, n_terms=n_terms)
    part3 = run_rank_crank_schur_obstruction(lib)
    part4_math = run_tau_and_cubic_agm(m_tau=500, n_agm=100)
    part4_lean = run_three_lab_lean4_audit()
    part5_r3 = run_r3_negative_controls()

    payload: dict[str, Any] = {
        "probe_id": "AUDIT-045",
        "arm": "R4-2",
        "title": "Ramanujan Mock Modular Shadows, Rank-Crank Schur Obstructions, 4-Tier Hankel/Euler-Witt Filtration & 3-Lab Lean 4 Forensics",
        "oracle_class": "exact+anchor",
        "honest_novelty_claim": "N1",
        "zero_floats_certified": True,
        "part1_mock_theta_and_appell_lerch": part1,
        "part2_four_tier_hankel_euler_witt_filtration": part2,
        "part3_rank_crank_schur_obstruction": part3,
        "part4_tau_and_cubic_theta_agm": part4_math,
        "part4_three_lab_lean4_forensics": part4_lean,
        "part5_r3_negative_controls": part5_r3,
    }
    verify_no_floats(payload)
    canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["canonical_sha256"] = hashlib.sha256(canonical_bytes).hexdigest()

    if write_certificate:
        out_path = Path(__file__).resolve().parent / "ramanujan_mock_shadows_certificate.json"
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    write_cert = "--write-cert" in args
    result = run_all_probes(write_certificate=write_cert)
    summary = {
        "probe_id": result["probe_id"],
        "honest_novelty_claim": result["honest_novelty_claim"],
        "zero_floats_certified": result["zero_floats_certified"],
        "part1_identities_ok": result["part1_mock_theta_and_appell_lerch"]["identities_all_verified"],
        "part2_law3_refuted_additive": result["part2_four_tier_hankel_euler_witt_filtration"]["law3_additive_hankel_refutation"]["theta3_vs_partial_theta_shifted_H12_exact_ratio_2"],
        "part2_ode_ok": result["part2_four_tier_hankel_euler_witt_filtration"]["tier3_ramanujan_ode_all_exact_zero_residual"],
        "part3_p5_S_shadow": result["part3_rank_crank_schur_obstruction"]["by_prime"]["p=5"]["S_shadow_ranks_by_rem"],
        "part3_p7_S_shadow": result["part3_rank_crank_schur_obstruction"]["by_prime"]["p=7"]["S_shadow_ranks_by_rem"],
        "part3_p11_S_shadow": result["part3_rank_crank_schur_obstruction"]["by_prime"]["p=11"]["S_shadow_ranks_by_rem"],
        "part3_p13_S_shadow": result["part3_rank_crank_schur_obstruction"]["by_prime"]["p=13"]["S_shadow_ranks_by_rem"],
        "part3_mod11_class6_r_opt_x10000": result["part3_rank_crank_schur_obstruction"]["mod11_class6_shadow_certificate"]["r_opt_x10000"],
        "part3_mod11_class6_r_h4_x10000": result["part3_rank_crank_schur_obstruction"]["mod11_class6_shadow_certificate"]["r_h4_x10000"],
        "part4_tau_all_ok": result["part4_tau_and_cubic_theta_agm"]["tau"]["lehmer_nonzero_all_n"],
        "part4_cubic_agm_ok": result["part4_tau_and_cubic_theta_agm"]["cubic_theta_agm"]["a3_eq_b3_plus_c3"],
        "part4_lean_files_audited": result["part4_three_lab_lean4_forensics"]["total_lean_files_audited"],
        "part5_r3_controls": f"{result['part5_r3_negative_controls']['controls_passed']}/{result['part5_r3_negative_controls']['controls_total']}",
        "canonical_sha256": result["canonical_sha256"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
