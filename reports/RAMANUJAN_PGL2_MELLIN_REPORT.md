# Wave 2 Round 4 — Arm R4-3 Report: Ramanujan Continued Fractions ($PGL(2)$), Schur-Tridiagonal Hard-Core Transfer & Exact $\mathbb{Q}((\epsilon))$ Master-Theorem Regulator Equalizer (`AUDIT-046`)

**Oracle Class:** `exact` (pure Python 3 stdlib, `int` / `fractions.Fraction` only, zero floats, zero bare `assert`s, zero external writes)  
**Honest Law-4 Novelty Classification:** **`N1`** (clean-room zero-float executable unification connecting `SF-01` Schur-tridiagonal/Sylvester inertia, `SF-02` $PGL(2, \mathbb{Q}[[q]])$ transfer & cross-ratio invariance, `SF-03` quadratic $q$-adic lock-in, `SF-05` tropical 1-cochain peeling, and `SF-07` exact $\mathbb{Q}((\epsilon))$ regulator-net invariance vs. shift-anomaly refutation of divergent-series numerology; all classical theorems explicitly quarantined as `N0`).

---

## 1. Strict Law-4 Prior-Art Quarantine (`N0` Foundations Explicitly Credited)

| Prior Art (`N0` — Credited, Never Overclaimed) | Role & Boundary vs. Arm R4-3 |
|---|---|
| **Klein (1884 *Lectures on the Icosahedron*)** | Icosahedral polynomials $T(u), H(u), F(u)$, syzygy $T(u)^3 + 1728 u H(u)^5 = F(u)^2$, and $j(\tau)$ via icosahedral parameter. |
| **Rogers (1894), Ramanujan (1913/1916/1920), Schur (1917), Andrews (1976/1981)** | Rogers–Ramanujan identities $G(q), H(q)$, continued fractions $R(q), C(q), S(q)$, quintic identity $R^{-5} - 11 - R^5 = f(-q)^6 / (q f(-q^5)^6)$, and finite polynomial truncations. |
| **Baxter (1980 *Hard Hexagons: Exact Solution*)** | Exact solution of the hard-hexagon lattice gas via Rogers–Ramanujan $G(q), H(q)$ and critical activity $z_c^2 - 11 z_c - 1 = 0$. |
| **Hardy (1920 *Ramanujan's Master Theorem*; 1949 *Divergent Series*), Candelpergher (2017)** | Ramanujan's Master Theorem Mellin integral formula, Euler–Maclaurin / Bernoulli asymptotic constants, and Ramanujan summation shift anomaly $\int_0^1 f(x)\,dx$. |
| **Sylvester (1852), Bunch–Kaufman (1977), Farkas (1902), Karp (1978)** | Symmetric congruence inertia without eigenvalues/square-roots and linear/tropical cycle-mean duality. |

---

## 2. Exact Verified Results Across All 3 Pillars (`ramanujan_pgl2_mellin.py`)

### Pillar 1 — Unified $PGL(2, \mathbb{Q}[[q]])$ Transfer $\longleftrightarrow$ Schur-Tridiagonal Engine (`SF-01` $\equiv$ `SF-02` $\cap$ `SF-03`)
For any generalized continued fraction $K_N(q) = \frac{1}{d_0 + a_1/(d_1 + \dots + a_{N-1}/d_{N-1})}$, backward $1 \times 1$ Schur elimination on the skew-tridiagonal matrix $J_N(q)$ (diagonal $d_k$, superdiagonal $+a_k$, subdiagonal $-1$) matches the cumulative $PGL(2, \mathbb{Q}[[q]])$ transfer product $\Pi_N = M_0 M_1 \cdots M_{N-1}$ identically mod $q^{36}$:
1. **Rogers–Ramanujan $\tilde{R}(q) = H(q)/G(q)$:**
   - **3-Way Exact BigInt Identity mod $q^{36}$:** Full-depth Schur determinant $\det(J_{36}(q)) \equiv G_{\mathrm{sum}}(q) \equiv G_{\mathrm{prod}}(q)$ (`[1, 1, 1, 1, 2, 2, 3, 3, 4, 5, 6, 7, ...]`) and minor $\det(J_{36}[1:,1:]) \equiv H_{\mathrm{sum}}(q) \equiv H_{\mathrm{prod}}(q)$ (`[1, 0, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, ...]`).
   - **Linear vs. Quadratic $q$-adic Lock-In Separation ($N = 3..7$):** While individual Schur denominator $B_N(q)$ locks to $G(q)$ at linear order $O(q^N)$ (`first_diff == N`), the transfer determinant $\det \Pi_N(q) = (-1)^N q^{\binom{N}{2}}$ drives projective cancellation so that the quotient $A_N(q)/B_N(q)$ locks to $\tilde{R}(q)$ at **quadratic order $O(q^{N(N+1)/2})$** (`first_diff = 6, 10, 15, 21, 28`, locking all `36` coefficients by $N = 8$!).
   - **Exact 4-Point Cross-Ratio Invariance & Consecutive-Convergent Closed Rational Law (`SF-02`, `R4-P03`):** Verified identically as a polynomial null-equivalence in $\mathbb{Q}[[q]]/(q^{36})$ under $\Pi_6(q)$ AND at $q = 1/3$ (`4/7`), **PLUS** the exact closed-form rational consecutive-convergent cross-ratio law $\mathrm{CR}(C_n, C_{n+1}; C_{n+2}, C_{n+3}) = \frac{d_{n+1} d_{n+2}}{d_{n+1} d_{n+2} + a_{n+2}}$ verified over $\mathbb{Q}$ for $n = 1..5, q \in \{1/3, 2/5\}$ across ALL THREE continued fractions:
     - Rogers–Ramanujan: $\frac{1}{1 + q^{n+2}}$ (recovering exact $q = (\mathrm{CR}_n^{-1}-1)/(\mathrm{CR}_{n-1}^{-1}-1)$ purely from $PGL(2)$-invariant ratios!);
     - Ramanujan Cubic: $\frac{1}{1 + q^{n+2} + q^{2(n+2)}}$;
     - Göllnitz–Gordon: $\frac{(1+q^{2n+3})(1+q^{2n+5})}{(1+q^{2n+3})(1+q^{2n+5}) + q^{2n+4}}$.
     *(Honest Law-4 note: the general identity follows directly from $PGL(2)$ transfer invariance / Euler–Wallis theory, cleanly scoped as `N1` alongside `RAMANUJAN_PORTALS_R4.md` `R4-N0-01..17` and read-only Mellin touchpoints `anthropics/formal-math@16a5ce4` `MellinCalculus.lean` & `openai/math@4eaee875` `ArithmeticMellinKernel.lean`.)*
   - **Exact Quintic Identity, Klein Syzygy & Leech $\Lambda_{24}$ Bridge (`AUDIT-031`/`042`):** Verified $\tilde{R}(q)^{-5} - 11q - q^2\tilde{R}(q)^5 = (q;q)_\infty^6/(q^5;q^5)_\infty^6 \pmod{q^{36}}$, exact syzygy $T(u)^3 + 1728 u H(u)^5 = F(u)^2$ ($u = q\tilde{R}^5$), and exact two-oracle BigInt parity between $j(\tau) = T(u)^3/(-u H(u)^5)$ and $E_4(q)^3/\Delta(q)$ yielding **`[1, 744, 196884, 21493760, 864299970, 20245856256, 333202640600, 4252023300096]`**!
   - **Exact Algebraic Obstructions:** At $q = 1$, $M(1)$ fixed points obey $z^2 + z - 1 = 0$ (discriminant `5`, non-square in $\mathbb{Q}$, obstructed in $\mathbb{P}^1(\mathbb{Q})$); Klein's vertex polynomial $H(u) = u^2 + 11u - 1$ satisfies $-z^2 H(1/z) \equiv z^2 - 11z - 1$, identically Baxter's 1980 hard-hexagon critical polynomial!
2. **Ramanujan Cubic $\tilde{C}(q)$ & Göllnitz–Gordon $\tilde{S}(q)$:** Both verified to exact $PGL(2) \equiv \text{Schur-tridiagonal} \equiv \text{infinite product} \pmod{q^{36}}$ and exact 4-point cross-ratio polynomial invariance!

### Pillar 2 — Hard-Core Lattice Transfer Matrices, Exact Inertia Perron Brackets & Tropical 1-Cochain Peeling (`SF-01` $\cap$ `SF-05`)
- **Exact $\mathbb{Z}_2$ Reflection Schur Block Reduction:** Verified $T_2(z) Q_2 = Q_2 \operatorname{diag}\!\left(\begin{pmatrix}1 & 2z \\ 1 & z\end{pmatrix}, [-z]\right)$ and $T_3(z) Q_3 = Q_3 \operatorname{diag}(B_3^{\mathrm{even}}(4\times 4), [-z])$ identically at $z \in \{1, 2, 11\}$.
- **Zero-Float Symmetric Inertia Perron Brackets ($\lambda W - W A_W W$):** Without computing a single float or square root, exact $\mathbb{Q}$ Bunch–Kaufman congruence inertia certifies:
  - $W = 1, z = 1$ ($\varphi$): `(207/128, 1657/1024)` (`width = 1/1024`, inertia `[1,0,1]` vs `[2,0,0]`);
  - $W = 2, z = 1$ ($1+\sqrt{2}$): `(309/128, 2473/1024)` (`width = 1/1024`, inertia `[2,0,1]` vs `[3,0,0]`);
  - $W = 3, z = 1$: `(1859/512, 465/128)` (`width = 1/512`, inertia `[4,0,1]` vs `[5,0,0]`);
  - $W = 3, z = 11$: `(5575/128, 44625/1024)` (`width = 25/1024`, inertia `[4,0,1]` vs `[5,0,0]`).
- **Exact Tropical / Quotient-LP 1-Cochain Peeling (`AUDIT-029` / `AUDIT-043`):** On width-3 states `[000, 100, 010, 001, 101]`, naive single-column max weight is `2`; coboundary potential $\phi = [0, 0, 0, 0, -1/2]$ shifts ALL allowed transition weights down to $\le \mathbf{3/2}$, matching the tight staggered 2-cycle `101 <-> 010` mean `(1+2)/2 = 3/2` with exact strong duality and strict separation **`3/2 < 2`**!

### Pillar 3 — Exact $\mathbb{Q}((\epsilon))$ Ramanujan Master Theorem, Regulator-Net Equalizer & Shift-Anomaly Refutation of `1+2+3+...=-1/12` Folklore (`SF-07`)
- **Two-Oracle Exact Bernoulli & Faulhaber Check:** Exact recurrence $B_0..B_{12}$ matches Laurent inversion of $(e^x - 1)/x$ bit-for-bit; exact Faulhaber identities verified for $k = 0..5, N = 1..8$.
- **Exact Shift-Anomaly Theorem (Refuting Pop-Math `1+2+3+...=-1/12` Numerology):** For EVERY $k \in \{0..5\}$, Ramanujan summation $\mathfrak{R}(n^k) = \zeta(-k)$ is linear yet **violates index-shift invariance by the exact non-zero integral**:
  $$\mathfrak{R}((n+1)^k) - \big(\mathfrak{R}(n^k) - 1\big) \;=\; \frac{1}{k+1} \;=\; \int_0^1 x^k\,dx \;\neq\; 0 \qquad \left(k=1:\; -\frac{7}{12} - \left(-\frac{13}{12}\right) = +\frac{1}{2}\right).$$
  Any heuristic "proof" that shifts and subtracts divergent series silently assumes both linearity and index-shift invariance — algebraically impossible!
- **Observer-Net Regulator Equalizer (Session 1 Pair 30):** Across `4` wildly differing normalized multiplicative cutoffs $\eta(\epsilon n) = \sum_i w_i e^{-\lambda_i \epsilon n}$ ($\sum w_i = 1$), the divergent $\epsilon^{-(k+1)}$ pole varies wildly (at $k=1$: **`1`**, **`9/49`**, **`7/4`**, **`2659/450`**), **YET** the finite $\epsilon^0$ Mellin-pole constant term equals **$\zeta(-k) = -B_{k+1}/(k+1)$ IDENTICALLY** across all 4 nets (`-1/12` at $k=1$). Conversely, breaking multiplicative scaling with shifted cutoff $e^{-\epsilon(n+\alpha)}$ mixes the pole into $\epsilon^0$ by exact $+\alpha^2/2$ (`alpha = 0, 1/2, 1, 2 -> -1/12, +1/24, +5/12, +23/12`)!
- **Exact $\mathbb{Q}$ Ramanujan Master Theorem & Mellin Scale Equivariance:** Verified $\operatorname{Res}_{s=-n}(\Gamma(s)\phi(-s)) = \frac{(-1)^n}{n!}\phi(n) = [x^n]f(x)$ identically for `n = 0..9` across `4` exact rational families (`exp(-x)`, `(1+x)^{-3/2}`, `(1-exp(-x))/x`, `exp(-7x/3)`) plus exact Mellin scaling $M\{D_\lambda f\}(s) = \lambda^{-s} M\{f\}(s)$!

---

## 3. Repro Commands, Verified Receipts & Falsification Criteria

Run from `symbiosis/round4/ramanujan-pgl2-mellin/`:

```bash
for m in "-I -B" "-I -O -B" "-I -B -W error" "-I -O -B -W error"; do
  python3 $m ramanujan_pgl2_mellin.py --json | sha256sum
  python3 $m test_ramanujan_pgl2_mellin_r5.py
done

PYTHONPATH=../../../publish/aletheia python3 -B -W error -m aletheia mutate ramanujan_pgl2_mellin.py \
  --test-cmd "python3 test_ramanujan_pgl2_mellin_r5.py" --work-root . --json

PYTHONPATH=../../../publish/aletheia python3 -B -W error -m aletheia audit-check . \
  --scripts ramanujan_pgl2_mellin.py test_ramanujan_pgl2_mellin_r5.py --json
```

**Verified Receipts:**
- `ramanujan_pgl2_mellin.py --json`: `4/4` isolated `-I` R4 bit-identical SHA-256 `87d6114b78b28dd95b04b1fe31ba48125907c93a05ece7d7f324e81cb38e9b48`
- `aletheia mutate ramanujan_pgl2_mellin.py`: **`18/18 = 100.0%` KILLED, `0` survivors**
- `aletheia audit-check`: **`PASS`** (`3` files, `0` CRLF, `0` `__pycache__`, `0` leaks, `0` bare `assert`s, `2/2` isolated R4 bit-identical)

**Falsification Criteria:**
- Falsified if ANY 3-way continued-fraction/Schur/product parity, quadratic lock-in exponent $N(N+1)/2$, 4-point cross-ratio identity, Ramanujan quintic identity, Klein syzygy, or BigInt $j(\tau)$ parity fails mod $q^{36}$ / $q^{16}$;
- Falsified if ANY $\mathbb{Z}_2$ Schur block identity, Bunch–Kaufman Perron inertia bracket, or $W=3$ tropical peeling bound (`3/2 < 2`) disagrees with independent SymPy eigenvalues/LP;
- Falsified if ANY Bernoulli/Faulhaber/shift-anomaly/regulator-equalizer/RMT identity fails, ANY mutant survives (`18/18`), or ANY R4/`audit-check` gate fails.
