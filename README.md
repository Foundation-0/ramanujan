# `Foundation-0/ramanujan`

> *"An equation for me has no meaning unless it expresses a thought of God."* — **Srinivasa Ramanujan** (1887–1920)
>
> Dedicated in deep scientific respect to **Srinivasa Ramanujan** — honoring his mathematical legacy through **exact, coordinate-free, machine-checkable pure-stdlib verification instruments**, stripping away numerology and `1 + 2 + 3 + ... = -1/12` folklore, and separating classical prior art (`N0`) from verified structural unifications (`N1`) and open unifying conjectures (`N2`).

`ramanujan` is a **zero-dependency, pure Python 3 standard-library** (`int`, `fractions.Fraction`) verification suite bridging four independently verified strands of Ramanujan mathematics under one exact algebraic lens (**Schur-complement fiber elimination, Krein inertia, $PGL(2, \mathbb{Q}[[q]])$ cross-ratio invariance, Euler–Witt Hankel filtrations, and exact integer orthogonality**):

- **Zero required third-party dependencies** (pure Python 3 stdlib `>=3.10` runs all 4 modules and `ramanujan verify`; optional `numpy` extra `pip install -e '.[sampled]'` enables `btz_graphs` Part C2's sampled float64 Monte Carlo $G$ & 400×24 quantization benchmark)
- **Zero bare `assert`s** (every verification gate remains active under `python3 -O`)
- **Explicit float / sampled accounting:** `mock_shadows`, `pgl2_mellin`, and `btz_graphs` Parts A/B/C1/D (or `--exact-only`) emit `0` JSON floats (`exact_math_zero_floats: true`). `btz_graphs` Part C2 (when `numpy` is installed, `30` float64 fields) and `sums_mixers` float64 DCT-II / mirage contrasts (`11` diagnostic float fields) are explicitly labeled as sampled/diagnostic floats (`exact_math_zero_floats: false`, never overstated as zero-float)
- **Bit-identical deterministic receipts** across all 4 isolated interpreter modes (`-I -B`, `-I -O -B`, `-I -B -W error`, `-I -O -B -W error`)
- **Strict Epistemic Honesty (Law 4 & Law 5):** Every classical theorem (`R4-N0-01`–`R4-N0-17`) is explicitly quarantined as `N0` prior art. All four bundled modules are honestly classified **`N1`**; we deliberately reserve any *"The Ramanujan Theorem"* title for a future, independently audited **`N2`** unification (see [Open `N2` Proof Program](#open-n2-proof-program-toward-the-ramanujan-theorem)).

---

## Quickstart

```bash
# List all 4 verified modules (runs cleanly from a fresh clone; or `pip install -e .` first)
PYTHONPATH=. python3 -s -B -m ramanujan list

# Run all 4 verified modules and print canonical SHA-256 receipts
PYTHONPATH=. python3 -s -B -m ramanujan verify

# Emit canonical JSON receipt bundle
PYTHONPATH=. python3 -s -B -m ramanujan verify --json

# Run the full isolated (-I) master verification & R5 test suite (all 4 modules + 4 R5 suites + CLI checks)
python3 -I -B tests/run_all.py
```

---

## Verified Modules & Audit Receipts

| Module | Audit & Status | Oracle Class | Verified Exact Core Results | Report |
|---|---|---|---|---|
| `ramanujan.btz_graphs` | `AUDIT-044` (`VERIFIED`, `N1`) | `exact+sampled+anchor` | Zero-float integer Ramanujan certifier $4(d-1)I - A_\perp^2 \succeq 0$ via Bareiss/Descartes inertia across `9` base graphs and ALL **`840` $H^1(G, \mathbb{Z}_2)$ signed 2-lift classes** (incl. `Dumbbell14` `196/256` Ramanujan lifts & integer witnesses); odd/even 2-mouth BTZ wormhole holonomy parity & balanced Krein signature $(k, |B|-2k, k)$; exact `24` Niemeier lattice $\Theta_L = E_4^3 - c_L \Delta$ universal $m_{\mathrm{cap}}$ (`2, 6, 13, 26, 53, 214`) & Milnor isospectral quantization split. | [RAMANUJAN_BTZ_REPORT.md](reports/RAMANUJAN_BTZ_REPORT.md) |
| `ramanujan.mock_shadows` | `AUDIT-045` (`VERIFIED`, `N1`) | `exact+anchor` (`0` JSON floats) | Pure-integer library of all `7` 3rd-order, `10` 5th-order, and `3` 7th-order Deathbed mock theta functions + Gordon–McIntosh $g_2, g_3$ + Watson–Zwegers Appell–Lerch identities ($O(q^{70})$); Law-3 refutation of naive additive Hankel separation ($\vartheta_3 = 2\Theta_+ - 1$); **4-tier Euler–Witt Hankel filtration** capturing mock-shadow cancellation rank collapse (`2, 4, 5, 6`, period-20 `20 < 22`) vs. shadow-doubling & null-shuffled controls; Rank–Crank column-space Schur complement $S_{\mathrm{shadow}}(p, r)$ Legendre selection at $p=5,7$ and genus-1 explosion at $p=11$ ($O(5, \mathbb{Q})$ invariant); BigInt $\tau(1..500)$ (`7/7` congruences, integer Deligne bound, Lehmer non-vanishing) & Borwein cubic AGM $a^3 = b^3 + c^3$. *(Sealed 20-file 3-lab Lean 4 forensics record archived in `certificates/ramanujan_mock_shadows_certificate.json`.)* | [RAMANUJAN_MOCK_SHADOWS_REPORT.md](reports/RAMANUJAN_MOCK_SHADOWS_REPORT.md) |
| `ramanujan.pgl2_mellin` | `AUDIT-046` (`VERIFIED`, `N1`) | `exact` (`0` JSON floats) | Unified $PGL(2, \mathbb{Q}[[q]]) \leftrightarrow$ Schur-tridiagonal engine for Rogers–Ramanujan $\tilde{R}(q)$, Cubic $\tilde{C}(q)$, and Göllnitz–Gordon $\tilde{S}(q)$ (3-way exact $G, H$ mod $q^{36}$, consecutive convergent cross-ratio law, quintic & Klein icosahedral syzygy $\to$ exact BigInt $j(\tau)$, Baxter $z^2 - 11z - 1$); width-$1,2,3$ hard-core $\mathbb{Z}_2$ Schur blocks (`4x4 + 1x1` at $W=3$) + Sylvester inertia Perron brackets + tropical peeling `3/2 < 2`; exact $\mathbb{Q}((\epsilon))$ **Shift-Anomaly Theorem** ($\frac{1}{k+1}$, refuting naive `1+2+3+...=-1/12`), 4-net Regulator Equalizer ($\zeta(-k)$), and exact Ramanujan Master Theorem / Mellin scale equivariance. | [RAMANUJAN_PGL2_MELLIN_REPORT.md](reports/RAMANUJAN_PGL2_MELLIN_REPORT.md) |
| `ramanujan.sums_mixers` | `AUDIT-048R` (`VERIFIED`, `N1`) | `exact+anchor` | Pure-integer Ramanujan subspace projectors $P_q = M_q / 24$ (`24/24` cyclic-shift equivariance vs. `2016.0` float64 DCT-II drift; exact $C=10^{30}$ DC gauge invariance vs. 100% float64 erasure at $10^{18}$); coordinate-free BFS 2-coloring exact integer PSD Ramanujan certifier (relabeling-invariant, odd-cycle-rejecting) + `48`-gate Pythagorean `20-21-29` Givens Two-Condition Spectral + Ordered-Layer Mixer Obstruction (`(0,1,3,7)` vs. colliding Ramanujan `(0,1,4,6)` vs. bottleneck); exact CF bracketing (`gap = 1/1007937474707144521`), Pell residual (`+1 != 0` on $F_{41}/F_{40}$ & $\sqrt{2}$ float64 bit-collisions), and Heegner `640320^3 + 744` attribution. | [RAMANUJAN_SUMS_MIXERS_REPORT.md](reports/RAMANUJAN_SUMS_MIXERS_REPORT.md) |

See [docs/RAMANUJAN_PORTALS_R4.md](docs/RAMANUJAN_PORTALS_R4.md) for the complete cross-domain portal map and commit-pinned formal-math touchpoints (`google-deepmind/formal-conjectures`, `openai/math`, `anthropics/flt`, `anthropics/formal-math`).

---

## Strict Law-4 `N0` Prior-Art Quarantine

All classical and modern foundations verified as baselines inside this repository are explicitly quarantined as **`N0` prior art** (never claimed as new; see `R4-N0-01`–`R4-N0-17` in [docs/RAMANUJAN_PORTALS_R4.md](docs/RAMANUJAN_PORTALS_R4.md)):

- **Modular Forms, Partitions & Mock Thetas:** Ramanujan (1913, 1916, 1918, 1919, 1920), Mordell (1917), Hardy (1920), Hecke (1937), Dyson (1944), Atkin–Swinnerton-Dyer (1954), Deligne (1974), Andrews (1976), Andrews–Garvan (1988), Borwein–Borwein (1991), Zwegers (2002), Dabholkar–Murthy–Zagier (2012), Cheng–Duncan–Harvey (2014).
- **Continued Fractions, Hard-Hexagon & Mellin Calculus:** Rogers (1894), Mellin (1902), Kronecker (1881), Stieltjes (1894), Baxter (1980).
- **Ramanujan Graphs, Signed 2-Lifts & Ramanujan Subspaces:** Lubotzky–Phillips–Sarnak (1988), Margulis (1988), Alon–Boppana (1991), Bilu–Linial (2006), Vaidyanathan (2014), Marcus–Spielman–Srivastava (2015).

---

## Open `N2` Proof Program Toward *The Ramanujan Theorem*

Following the same naming discipline as [`Foundation-0/hawking`](https://github.com/Foundation-0/hawking), we do **not** declare a *"Ramanujan Theorem"* prematurely. The four verified `N1` instruments above reveal a concrete, falsifiable **`N2` unification target** now under investigation:

1. **Unified Schur-Elimination Spectral-Obstruction Law:** Unify (i) signed 2-lift Ramanujan spectral certification $4(d-1)I - A_\chi^2 \succeq 0$ (`btz_graphs`), (ii) rank-crank column-space Schur shadows $S_{\mathrm{shadow}}(p, r)$ and Euler–Witt mock-shadow cancellation collapse (`mock_shadows`), (iii) $PGL(2, \mathbb{Q}[[q]])$ tridiagonal Schur peeling & cross-ratio towers (`pgl2_mellin`), and (iv) integer Ramanujan-sum $c_q(n)$ orthogonal Schur projectors (`sums_mixers`) under a single coordinate-free exact theorem with zero counterexamples across unseen primes, moduli, and finite graphs.
2. **Formal Proof Upgrade:** Machine-check the resulting universal statement over $\mathbb{Q}/\mathbb{Z}$ with independent zero-shared-code verification and Lean 4 formalization (`0` `sorry`, `0` `axiom`, `0` `native_decide`).

---

## License

[MIT](LICENSE)
