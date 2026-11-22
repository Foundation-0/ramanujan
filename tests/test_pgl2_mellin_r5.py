#!/usr/bin/env python3
"""
R1-R5 Mutation-Killing Verification Suite for `ramanujan_pgl2_mellin.py`.

Exercises all power-series validators, PGL(2)/Schur-tridiagonal parity, exact symmetric
Bunch-Kaufman inertia (1x1 and 2x2 hyperbolic pivots), hard-core transfer/peeling bounds,
Bernoulli/Laurent/Mellin invariants, and fail-closed boundary guards targeting 100.0%
kill rate via `aletheia mutate`.

Zero bare `assert`s; R4-clean under `-I -B`, `-I -O -B`, `-I -B -W error`, `-I -O -B -W error`.
"""
from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ramanujan import pgl2_mellin as rpm  # noqa: E402


def require_cond(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(f"TEST_FAILED: {msg}")


def expect_raises(
    exc_cls: type[BaseException],
    fn: Callable[[], Any],
    label: str,
    match: str | None = None,
) -> None:
    try:
        fn()
    except exc_cls as exc:
        if match is not None and match not in str(exc):
            raise RuntimeError(f"UNEXPECTED_MSG ({label}): {exc!r} missing {match!r}")
        return
    raise RuntimeError(f"EXPECTED_{exc_cls.__name__}_NOT_RAISED: {label}")


def run_all_tests() -> int:
    groups = 0

    # 1. Exact Q[[q]] power series, PGL(2) transfer, and Schur-tridiagonal guards
    expect_raises(ValueError, lambda: rpm.ps_const(Fraction(1), 0), "mod < 1", match="mod")
    expect_raises(ValueError, lambda: rpm.ps_const(Fraction(1), True), "mod bool", match="mod")  # type: ignore[arg-type]
    require_cond(rpm.ps_const(Fraction(3), 1) == [Fraction(3)], "mod == 1 boundary ok")

    expect_raises(ValueError, lambda: rpm.ps_inv([Fraction(0), Fraction(1)], 2), "non-invertible a0=0", match="invertible")
    expect_raises(ValueError, lambda: rpm.ps_inv([Fraction(1)], 2), "short series inv", match="invertible")
    expect_raises(ValueError, lambda: rpm.ps_pow([Fraction(1), Fraction(1)], -1, 2), "neg exp", match="exponent")
    expect_raises(ValueError, lambda: rpm.ps_pow([Fraction(1), Fraction(1)], True, 2), "bool exp", match="exponent")  # type: ignore[arg-type]
    require_cond(rpm.ps_pow([Fraction(2), Fraction(3)], 0, 2) == [Fraction(1), Fraction(0)], "exp == 0 ok")

    expect_raises(ValueError, lambda: rpm.q_pochhammer(0, 1, 4), "poch start < 1", match="step_start")
    expect_raises(ValueError, lambda: rpm.q_pochhammer(1, 0, 4), "poch step < 1", match="step_start")
    require_cond(rpm.q_pochhammer(1, 1, 4) == [Fraction(1), Fraction(-1), Fraction(-1), Fraction(0)], "poch(1,1,4) ok")

    expect_raises(ValueError, lambda: rpm.pgl2_transfer_product([], [], 4), "empty d_seq pgl2", match="d_seq")
    expect_raises(ValueError, lambda: rpm.pgl2_transfer_product([[Fraction(1)]], [[Fraction(1)]], 1), "bad a_seq pgl2", match="d_seq")
    expect_raises(ValueError, lambda: rpm.schur_tridiagonal_cf([], [], 4), "empty d_seq schur", match="d_seq")
    expect_raises(ValueError, lambda: rpm.schur_tridiagonal_cf([[Fraction(1)]], [[Fraction(1)]], 1), "bad a_seq schur", match="d_seq")
    k1, a1, b1 = rpm.schur_tridiagonal_cf([[Fraction(2)]], [], 1)
    require_cond(k1 == [Fraction(1, 2)] and a1 == [Fraction(1)] and b1 == [Fraction(2)], "N=1 schur base")
    require_cond(rpm.ps_first_diff_order([Fraction(1)], [Fraction(1)], 1) is None, "identical series diff is None")

    # Test direct pgl2_apply_ps & ps_cross_ratio on invertible unit-det matrix [[2, 1], [1, 1]]
    m4 = 4
    mat_u = (
        rpm.ps_const(Fraction(2), m4),
        rpm.ps_const(Fraction(1), m4),
        rpm.ps_const(Fraction(1), m4),
        rpm.ps_const(Fraction(1), m4),
    )
    zs = [rpm.ps_const(Fraction(k), m4) for k in (1, 2, 4, 7)]
    mzs = [rpm.pgl2_apply_ps(mat_u, z, m4) for z in zs]
    require_cond(
        rpm.ps_cross_ratio(zs[0], zs[1], zs[2], zs[3], m4)
        == rpm.ps_cross_ratio(mzs[0], mzs[1], mzs[2], mzs[3], m4),
        "pgl2_apply_ps cross-ratio invariant",
    )
    groups += 1

    # 2. Exact symmetric Bunch-Kaufman inertia, hard-core strip width, Bernoulli & Laurent guards
    expect_raises(ValueError, lambda: rpm.exact_symmetric_inertia_q([]), "empty mat", match="square")
    expect_raises(ValueError, lambda: rpm.exact_symmetric_inertia_q([[Fraction(1), Fraction(2)]]), "non-square mat", match="square")
    expect_raises(
        ValueError,
        lambda: rpm.exact_symmetric_inertia_q([[Fraction(1), Fraction(2)], [Fraction(3), Fraction(1)]]),
        "non-symmetric mat",
        match="symmetric",
    )
    # Test 2x2 hyperbolic pivot [[0, 2], [2, 0]] + zero block [[0, 0], [0, 0]] + swapped pivot
    require_cond(rpm.exact_symmetric_inertia_q([[Fraction(0), Fraction(2)], [Fraction(2), Fraction(0)]]) == (1, 0, 1), "2x2 hyperbolic inertia")
    require_cond(rpm.exact_symmetric_inertia_q([[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]) == (0, 2, 0), "2x2 zero inertia")
    require_cond(
        rpm.exact_symmetric_inertia_q([
            [Fraction(0), Fraction(0), Fraction(0)],
            [Fraction(0), Fraction(0), Fraction(3)],
            [Fraction(0), Fraction(3), Fraction(0)],
        ]) == (1, 1, 1),
        "3x3 shifted 2x2 hyperbolic pivot",
    )
    require_cond(
        rpm.exact_symmetric_inertia_q([
            [Fraction(0), Fraction(0), Fraction(1)],
            [Fraction(0), Fraction(0), Fraction(2)],
            [Fraction(1), Fraction(2), Fraction(0)],
        ]) == (1, 1, 1),
        "3x3 q-swap hyperbolic pivot",
    )

    expect_raises(ValueError, lambda: rpm._hardcore_states(0), "width < 1", match="width")
    expect_raises(ValueError, lambda: rpm._hardcore_states(7), "width > 6", match="width")
    expect_raises(ValueError, lambda: rpm._hardcore_states(True), "width bool", match="width")  # type: ignore[arg-type]
    require_cond(len(rpm._hardcore_states(1)) == 2 and len(rpm._hardcore_states(6)) == 21, "width 1 and 6 boundaries ok")
    expect_raises(ValueError, lambda: rpm.exact_perron_bracket(1, Fraction(1), Fraction(3), Fraction(4)), "bad lower bound already PSD", match="lower bound")
    expect_raises(ValueError, lambda: rpm.exact_perron_bracket(1, Fraction(1), Fraction(1), Fraction(1)), "bad upper bound not PSD", match="upper bound")

    expect_raises(ValueError, lambda: rpm.exact_bernoulli_numbers(-1), "neg max_n", match="max_n")
    expect_raises(ValueError, lambda: rpm.exact_bernoulli_numbers(True), "bool max_n", match="max_n")  # type: ignore[arg-type]
    require_cond(rpm.exact_bernoulli_numbers(0) == [Fraction(1)], "max_n == 0 boundary ok")

    b4 = rpm.exact_bernoulli_numbers(4)
    expect_raises(ValueError, lambda: rpm._laurent_const_term_fk(-1, Fraction(1), b4), "neg k", match="k out of range")
    expect_raises(ValueError, lambda: rpm._laurent_const_term_fk(4, Fraction(1), b4), "k+1 >= len", match="k out of range")
    expect_raises(ValueError, lambda: rpm._laurent_const_term_fk(1, Fraction(0), b4), "lam <= 0", match="lam")
    require_cond(rpm._laurent_const_term_fk(3, Fraction(1), b4) == (Fraction(6), Fraction(1, 120)), "exact k=3 boundary ok")
    groups += 1

    # 3. Full end-to-end exact verification across all 3 Ramanujan pillars
    rep = rpm.run_all()
    p1 = rep["pillar_1_continued_fractions_pgl2_schur"]
    rr = p1["rogers_ramanujan"]
    require_cond(rr["pgl2_equals_schur_tridiagonal"] is True and rr["pgl2_equals_euler_product"] is True, "RR PGL2 == Schur == prod")
    require_cond(rr["G_3way_schur_det_eq_qsum_eq_product"] is True and rr["H_3way_schur_det_eq_qsum_eq_product"] is True, "G & H 3-way exact")
    require_cond(rr["quadratic_q_adic_lockin_all_exact"] is True, "RR quadratic lockin")
    require_cond(rr["pgl2_4pt_cross_ratio_poly_invariant"] is True and rr["pgl2_4pt_cross_ratio_at_q_third_invariant"] is True and rr["consec_convergent_cr_closed_law_exact"] is True, "RR cross-ratio & consec law")
    require_cond(rr["quintic_identity_exact_mod_q36"] is True and rr["klein_icosahedral_syzygy_exact"] is True, "RR quintic & Klein syzygy")
    require_cond(rr["j_tau_from_R_equals_E4_Delta_exact"] is True and rr["j_tau_coeffs_q_neg1_to_q6"][:4] == [1, 744, 196884, 21493760], "j(tau) exact BigInt match")
    require_cond(rr["baxter_critical_poly_equals_icosahedral_H_inv"] is True, "Baxter == Klein H(1/z)")
    require_cond(p1["ramanujan_cubic"]["pgl2_equals_schur_tridiagonal"] is True and p1["ramanujan_cubic"]["pgl2_equals_product_mod_q36"] is True and p1["ramanujan_cubic"]["pgl2_4pt_cross_ratio_poly_invariant"] is True and p1["ramanujan_cubic"]["consec_convergent_cr_closed_law_exact"] is True, "Cubic CF exact")
    require_cond(p1["gollnitz_gordon"]["pgl2_equals_schur_tridiagonal"] is True and p1["gollnitz_gordon"]["pgl2_equals_product_mod_q36"] is True and p1["gollnitz_gordon"]["pgl2_4pt_cross_ratio_poly_invariant"] is True and p1["gollnitz_gordon"]["consec_convergent_cr_closed_law_exact"] is True, "GG CF exact")

    p2 = rep["pillar_2_hardcore_transfer_inertia_peeling"]
    require_cond(p2["z2_symmetry_schur_block_exact"] is True, "Z2 Schur block exact")
    require_cond(all(b["certified_strict_bracket"] for b in p2["exact_perron_brackets"]), "all Perron brackets exact")
    require_cond(p2["tropical_cochain_peeling_w3"]["strong_duality_exact_match"] is True and p2["tropical_cochain_peeling_w3"]["strict_separation_3_2_lt_2"] is True, "W=3 peeling 3/2 < 2")

    p3 = rep["pillar_3_ramanujan_master_mellin_summation"]
    require_cond(rep["all_passed"] is True and rep["epistemic_status"] == "VERIFIED", "pgl2_mellin all_passed & VERIFIED")
    require_cond(p3["bernoulli_two_oracle_exact_match"] is True and p3["faulhaber_polynomial_exact_k0_to_k5"] is True, "Bernoulli & Faulhaber")
    require_cond(p3["shift_anomaly_theorem"]["all_exact_int_0_1_x_pow_k"] is True, "Shift anomaly exact")
    require_cond(p3["regulator_net_equalizer"]["const_term_invariant_across_all_4_nets_k0_to_k5"] is True, "Regulator equalizer inv")
    require_cond(p3["regulator_net_equalizer"]["divergent_poles_differ_across_nets"] is True, "Poles differ across nets")
    require_cond(p3["regulator_net_equalizer"]["shifted_cutoff_breakage_exact"] is True, "Shifted cutoff breakage exact")
    require_cond(
        p3["ramanujan_master_theorem"]["all_4_families_residue_parity_exact"] is True
        and p3["ramanujan_master_theorem"]["mellin_scale_equivariance_exact"] is True
        and p3["ramanujan_master_theorem"]["mellin_negative_controls_all_rejected"] is True,
        "RMT & non-tautological Mellin scale equiv + negative controls",
    )
    # Verify independent (1+x)^(-3/2) series satisfies f(x)^2 * (1+x)^3 == 1 mod x^10
    f_binom = rpm._ps_inv_sqrt_cube_1_plus_x(10)
    one_plus_x = [Fraction(1), Fraction(1)] + [Fraction(0)] * 8
    prod_id = rpm.ps_mul(rpm.ps_mul(f_binom, f_binom, 10), rpm.ps_pow(one_plus_x, 3, 10), 10)
    require_cond(prod_id == [Fraction(1)] + [Fraction(0)] * 9, "f^2 * (1+x)^3 == 1 exact")
    # Direct Mellin scale-equivariance input guards, boundary checks & must-fail controls
    expect_raises(ValueError, lambda: rpm._validate_positive_fraction(Fraction(0)), "lam == 0", match="lam")
    expect_raises(ValueError, lambda: rpm._validate_positive_fraction(Fraction(-1, 2)), "lam < 0", match="lam")
    expect_raises(ValueError, lambda: rpm._validate_positive_fraction(1), "lam non-Fraction", match="lam")
    expect_raises(ValueError, lambda: rpm._validate_pos_s(0), "s < 1", match="strict int")
    expect_raises(ValueError, lambda: rpm._validate_pos_s(True), "s bool", match="strict int")
    expect_raises(ValueError, lambda: rpm._validate_beta_ks(6, 0), "beta s < 1", match="1 <= s < k_exp")
    expect_raises(ValueError, lambda: rpm._validate_beta_ks(6, 6), "beta s == k_exp", match="1 <= s < k_exp")
    expect_raises(ValueError, lambda: rpm._validate_beta_ks(True, 1), "beta k bool", match="1 <= s < k_exp")
    # Length == 2 rejected and length == 3 boundary accepted for both RMT series extractors
    exp_len3 = [Fraction(1), Fraction(-2), Fraction(2)]
    require_cond(rpm._rmt_mellin_from_dilated_exp_series(exp_len3, 1) == Fraction(1, 2), "exp RMT len==3 boundary ok")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_exp_series([Fraction(1), Fraction(-2)], 1), "exp len < 3", match="length >= 3")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_exp_series([Fraction(0), Fraction(-1), Fraction(1)], 1), "exp phi0 == 0", match="leading RMT")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_exp_series([Fraction(1), Fraction(0), Fraction(0)], 1), "exp ratio == 0", match="positive")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_exp_series([Fraction(1), Fraction(1), Fraction(1, 2)], 1), "exp ratio < 0", match="positive")
    beta_len3 = [Fraction(1), Fraction(-6), Fraction(21)]
    require_cond(rpm._rmt_mellin_from_dilated_beta_series(beta_len3, 6, 1) == Fraction(1, 5), "beta RMT len==3 boundary ok")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_beta_series([Fraction(1), Fraction(-6)], 6, 1), "beta len < 3", match="length >= 3")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_beta_series([Fraction(0), Fraction(-6), Fraction(21)], 6, 1), "beta phi0 == 0", match="leading RMT")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_beta_series([Fraction(1), Fraction(0), Fraction(0)], 6, 1), "beta ratio == 0", match="positive")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_beta_series([Fraction(1), Fraction(6), Fraction(21)], 6, 1), "beta ratio < 0", match="positive")
    expect_raises(ValueError, lambda: rpm._rmt_mellin_from_dilated_beta_series([Fraction(1), Fraction(-6), Fraction(20)], 6, 1), "beta corrupt Pochhammer step", match="Pochhammer")

    expect_raises(ValueError, lambda: rpm.verify_mellin_scale_equivariance(Fraction(0)), "lam <= 0", match="lam")
    expect_raises(ValueError, lambda: rpm.verify_mellin_scale_equivariance(Fraction(7, 3), max_s=0), "max_s < 1", match="max_s")
    expect_raises(ValueError, lambda: rpm.verify_mellin_scale_equivariance(Fraction(7, 3), max_s=6), "max_s > 5", match="max_s")
    expect_raises(ValueError, lambda: rpm.verify_mellin_scale_equivariance(Fraction(7, 3), scale_exponent_sign=0), "bad sign", match="sign")
    expect_raises(ValueError, lambda: rpm.verify_mellin_scale_equivariance(Fraction(7, 3), corrupt_series_c1=Fraction(1, 5)), "corrupt series rejected", match="ratio")
    require_cond(rpm.verify_mellin_scale_equivariance(Fraction(7, 3), scale_exponent_sign=1)["all_exact"] is False, "wrong sign fails")
    require_cond(rpm.verify_mellin_scale_equivariance(Fraction(7, 3), scale_exponent_shift=1)["all_exact"] is False, "shifted exp fails")
    groups += 1

    return groups


if __name__ == "__main__":
    n = run_all_tests()
    print(f"ROUND4_RAMANUJAN_PGL2_MELLIN_R5_OK: {n}/3 test groups passed")
