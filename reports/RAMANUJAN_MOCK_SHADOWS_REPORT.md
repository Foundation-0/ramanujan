# Round 4 Arm R4-2 (`AUDIT-045`): Ramanujan Mock Modular Shadows, Rank–Crank Column-Space Schur Obstructions, 4-Tier Exact Hankel/Euler–Witt Filtration & 3-Lab Lean 4 Forensics

> **Audit ID:** `AUDIT-045` (`SF-01 #19` $\cap$ `SF-04` $\cap$ `SF-06`)  
> **Owner:** `spectral-prover` (Wave 2 — Round 4, Arm R4-2)  
> **Oracle Class:** `exact+anchor` (100% pure Python 3 stdlib `int` + `fractions.Fraction`; **ZERO floating-point arithmetic** anywhere in theorems or emitted JSON; **ZERO bare `assert` statements**)  
> **Honest Law-4 Novelty Rating:** **`N1`** (exact coordinate-free synthesis & algorithmic obstruction framework + explicit Law-3 refutation of naive additive-Hankel separation + commit-pinned 3-lab `aletheia v1.2.0` Lean 4 audit; zero inflated `N2` claims)  
> **External Governance:** Strictly **READ-ONLY** on all external repositories (`0` external PRs, issues, or comments).

---

## 0. Executive Summary

We construct a zero-float, zero-dependency exact $\mathbb{Z}[[q]] / \mathbb{Q}[[q]]$ formal power-series and exact rational linear-algebra probe (`ramanujan_mock_shadows.py` + `ramanujan_mock_shadows_certificate.json` + `test_r5_ramanujan_mock_shadows.py`) investigating Srinivasa Ramanujan's 1920 Deathbed mock theta functions, Lost Notebook $q$-series, Dyson rank vs. Andrews–Garvan crank partition congruences, Ramanujan's $\tau(n)$ & cubic theta AGM, and live 3-lab Lean 4 formalizations.

**Five Verified Results:**
1. **Complete Exact Mock Theta, Universal & Appell–Lerch Library (`Part 1`, $O(q^{70})$):** Pure-integer constructions of all **7** 3rd-order ($f, \phi, \psi, \chi, \omega, \nu, \rho$), all **10** 5th-order ($f_0.. \chi_0, f_1..\chi_1$), and all **3** 7th-order ($\mathcal{F}_0, \mathcal{F}_1, \mathcal{F}_2$) Ramanujan mock theta functions, Gordon–McIntosh universal mock thetas $g_2, g_3$ (`f(q) = 2 - 2 g_3(-1; q)`, `\omega(q) = g_3(q; q^2)`), and Watson–Zwegers bilateral Appell–Lerch identities (`(q;q)_\infty f(q) = 1 + 4\sum_{n\ge 1} \frac{(-1)^n q^{n(3n+1)/2}}{1+q^n}`, `(q^2;q^2)_\infty \omega(q) = \sum_{n\ge 0} (-1)^n q^{3n^2+3n}\frac{1+q^{2n+1}}{1-q^{2n+1}}`) — `11/11` exact identities verified with `0` residual.
2. **Law-3 Refutation of Naive Additive-Hankel Separation (`Part 2`, Counterexample Witness):** We prove explicitly that **additive Hankel minors $H_m(A)$ alone CANNOT separate modular forms from partial or mock thetas**:
   - Full modular $\vartheta_3(q) = 1 + 2\sum_{n\ge 1} q^{n^2}$ and partial theta $\Theta_+(q) = 1 + \sum_{n\ge 1} q^{n^2} = \frac{1}{2}(\vartheta_3(q) + 1)$ satisfy **$H_m^{(1)}(\vartheta_3) \equiv 2\,H_m^{(1)}(\Theta_+)$ identically** (verified at $m=12$, differing only by a rank-1 perturbation $-e_0 e_0^\top$ at $(0,0)$).
   - Partition log-concavity (Turán / DeSalvo–Pak) forces $\det H_2^{(s)}(p) = p(s)p(s+2) - p(s+1)^2 < 0$ for all $25 \le s \le 67$, proving even the positive modular $\eta$-quotient $1/\eta(q) = \sum p(n)q^n$ has strictly indefinite Hankel matrices ($n_- > 0$).
3. **4-Tier Exact Coordinate-Free Matrix-Minor Filtration (`Part 2`, `SF-01 #19`):**
   - **Tier 1 (Additive Hankel $H_{12}(A)$):** Separates rational/periodic series (`rational_fib`: exact rank `2`, inertia `(2, 10, 0)`) from all non-rational series (`rank = 12`).
   - **Tier 2 (Multiplicative Euler–Witt Exponent Hankel $H_m(b(A))$, $A(q)/a_0 = \prod_{k\ge 1}(1-q^k)^{-b_k}$):** Breaks additive-Hankel blindness completely! Periodic $\eta$-quotients saturate at exact finite rank (`eta1`, `1/eta1`, `Delta/q`: `1`; `theta4`, `C(-1;q)`: `2`; `theta3`: `3`) while `partial_theta` (`10 -> 14`), `false_pent` (`10 -> 14`), all individual mock thetas (`10 -> 14`), and all `CS-11` null-shuffled controls fail to saturate. **Mock-Shadow Cancellation Rank Collapse:** Individually non-saturating mock thetas (`10 -> 14`) collapse to exact finite periodic Euler–Witt rank under Zwegers-shadow-cancelling combinations (`f + 4\psi(-q) -> 2`, `\nu + q\omega(q^2) -> 4`, `(2\rho+\omega)/3 -> 4`, `(4\chi-f)/3 -> 5`, `f_0 + 2\psi_0(-q) -> 6`, `2\psi_1(-q) - f_1 -> 6`, and period-20 `\phi_0(-q^2) + \psi_0(q)` collapsing from `22 -> 20` at $m=22$), while wrong-sign shadow-doubling combinations (`f - 4\psi(-q)`, `\nu - q\omega(q^2)`, `\phi_0(-q^2) - \psi_0(q)`) stay **full rank** with exponentially exploding $b_k$.
   - **Tier 3 (Log-Derivative $H_8(c(A))^2$ `R_opt` vs. `R_{H4}` + Ramanujan ODE + Hecke Schur Closure):** Interior-zero modular forms ($E_4, E_6$) and quasimodular $E_2$ also have full Euler–Witt rank (`10 -> 14`), and **`R_opt` (`AUDIT-002`) suffers `CS-11` scalar-proxy blindness** (`R_opt \approx 1.0000`, `ceil = 2` on $E_4, E_6, E_2, f, f_0, \Psi_{\mathrm{pent}}$ alike). Upgrading to the exact 4th-moment 2-step Schur bound **`R_{H4}` (`AUDIT-014`)** strictly separates them: `\lceil R_{H4}\rceil = 3` (`E_4, E_6, E_2`) vs. `4` (`m3_f`, `m5_f0`) vs. `5` (`false_pent`) vs. `6` (`partial_theta`). Simultaneously, $E_2, E_4, E_6$ satisfy Ramanujan's 1916 ODE closure to $O(q^{70})$ (`0` residual), and $\Delta(q)$ satisfies exact Hecke–Gram Schur closure $S(\Delta, T_{p,12}\Delta) = 0$ ($p \in \{2,3,5\}$).
4. **Tier 4 — Exact Column-Space Rank–Crank Schur Complement $S_{\mathrm{shadow}}(p, r)$ (`Part 3`, $p \in \{5, 7, 11, 13\}$):**
   For palindromic difference matrices $A = W_{\mathrm{crank}}(p, r)$ and $B = W_{\mathrm{rank}}(p, r)$ ($h = (p-1)/2$), the exact rational Schur complement
   $$S_{\mathrm{shadow}}(p, r) \;:=\; B^\top B - B^\top A\,(A^\top A)^+\,A^\top B \;\in\; \mathbb{Q}^{h \times h}_{\succeq 0}$$
   obeys Haynsworth rank additivity $\operatorname{rank}(S_{\mathrm{shadow}}) = \operatorname{rank}([A \mid B]) - \operatorname{rank}(A)$ and captures the exact arithmetic phase transition across $p = 5, 7, 11, 13$:
   - **$p = 5, 7$ ($g(X_0(p)) = 0$):** $\operatorname{rank}(S_{\mathrm{shadow}}(p, r)) = \mathbf{1}\!\left[\left(\frac{1-24r}{p}\right) = +1\right]$ (`[1,0,0,1,0]` for $p=5$; `[1,0,1,0,0,0,1]` for $p=7$), matching all **3** Hickerson 7th-order mock theta rank-difference identities on the exact 3 QR classes `7k+{0, 2, 6}` to `22` terms with `0` residual.
   - **$p = 11$ ($g(X_0(11)) = 1$):** Crank retains $\operatorname{rank}(A) \le 1$ (`[1,1,1,1,1,1,0,1,1,1,1]`, exact `0` Parseval defect on `11k+6`), whereas Dyson rank explodes to **full rank `5`** on ALL 11 residue classes (`S_shadow = [5]*11`). On `11k+6`, $S_{\mathrm{shadow}}(11, 6)$ is strictly positive definite (`inertia = (5,0,0)`, all `5/5` leading Bareiss minors positive), strictly unmasked by **`R_{H4} \approx 2.0274` (`ceil = 3`) > `R_opt \approx 1.0000` (`ceil = 2`)**, and `0`-residual invariant under exact $O(5, \mathbb{Q})$ Householder orthogonal conjugation.
   - **$p = 13$ (no Ramanujan congruence):** Garvan's rank-1 crank collapse terminates; both crank and rank jump to full rank `6` with completely disjoint spans (`S_shadow = [6]*13`).
5. **Exact BigInt $\tau(n)$ (`n=1..500`), Borwein Cubic Theta AGM ($O(q^{100})$), & Commit-Pinned 3-Lab `aletheia v1.2.0 --lean-audit` Forensics (`Part 4`):**
   - Verified all 7 classical $\tau(n)$ congruences (`691`, Kolberg `2^11 = 2048` for all odd $n$, Swinnerton-Dyer `3^6 = 729` & `5^3 = 125`, `7`, Wilton `23` inert & split), `1,143` coprime Hecke pairs, `19` prime-power recursions, integer Deligne bound $\tau(p)^2 \le 4 p^{11}$ (`95` primes, max exact Sato–Tate ratio at $p=103$: `12741344527718757576976/13842338707244455781047`), and Lehmer $\tau(n) \neq 0$ (`1 \le n \le 500`).
   - Verified Borwein–Ramanujan cubic theta AGM $a(q)^3 = b(q)^3 + c(q)^3$ and both AGM step identities to $O(q^{100})$ + exact Euler–Witt Hankel ranks `3` (`b(q)`) and `2` (`\tilde{c}(q)/3`, zero-mean period-3 `[1,1,-2]`).
   - Audited **20 commit-pinned Lean 4 files** across 3 labs via live `aletheia v1.2.0`: `dm-math-formal-conjectures@d8d031d4` (`RamanujanTau.lean` Lean 4.22 `public import` + `3` `sorry`s including unfinished `@[category test] lemma τ_two : τ 2 = -24 := by sorry` at `L60` and real-power `(p : ℝ)^(11/2)` Petersson typing; `PartitionParity.lean` `16` `sorry`s; `Gourevitch.lean` `1` `sorry`), `openai-math@4eaee875` (**`15/15` `mathlib_clean`**, `0` `sorry`s, formalizing metaplectic Eisenstein-ring Ramanujan sums), and `anthropics-flt@6e837e75` (**`2/2` `mathlib_clean`**, `0` `sorry`s, proving Ramanujan's integer ODE system for `E2, E4, E6`).

---

## 1. Strict Law-4 `N0` Prior-Art Quarantine Table

Every classical and modern mathematical theorem used or verified in this probe is explicitly quarantined as **`N0`** below (consistent with `RAMANUJAN_PORTALS_R4.md` `R4-N0-01..17`). None of the following rows is claimed as `N1` or `N2`:

| Quarantine ID | Quarantined Result / Construction (`N0`) | Primary Attribution | Role in `AUDIT-045` |
|---|---|---|---|
| `R4-N0-01` | $\Delta(q)=q\prod(1-q^n)^{24}$, $\tau(n)$ multiplicativity, $\tau(n)\equiv\sigma_{11}(n)\pmod{691}$, congruences mod $2^{11}, 3^6, 5^3, 7, 23$, $|\tau(p)|\le 2p^{11/2}$ | Ramanujan (1916); Mordell (1917); Wilton (1930); Hecke (1937); Kolberg (1962); Swinnerton-Dyer (1973); Deligne (1974) | Pure-BigInt zero-float baseline (`Part 4`) |
| `R4-N0-02` | Partition congruences mod $5, 7, 11$; Dyson rank; Atkin–Swinnerton-Dyer & Atkin–Hussain rank differences; Andrews–Garvan crank & $p$-dissections; Hickerson 7th-order mock theta rank identities | Ramanujan (1919); Dyson (1944); Atkin–Swinnerton-Dyer (1954); Atkin–Hussain (1958); Garvan (1988); Andrews–Garvan (1988); Hickerson (1988) | Input generating functions for $S_{\mathrm{shadow}}(p, r)$ (`Part 3`) |
| `R4-N0-03` | 1920 Deathbed mock theta functions (orders 3, 5, 7), Watson identities, Lost Notebook, Gordon–McIntosh universal $g_2, g_3$, Zwegers Appell–Lerch / harmonic Maass shadows, Bringmann–Ono | Ramanujan (1920); Watson (1936, 1937); Andrews (1976); Zwegers (2002); Gordon–McIntosh (2003); Bringmann–Ono (2010) | Library & exact shadow-cancellation testbed (`Parts 1–2`) |
| `R4-N0-14` | Ramanujan's 1916 Eisenstein ODE system $(E_2, E_4, E_6)$ & Borwein cubic theta AGM $a(q)^3 = b(q)^3 + c(q)^3$ | Ramanujan (1916); Borwein–Borwein (1991) | Tier-3 ODE closure & `Part 4` exact baseline |
| `R4-N0-17` | Kronecker Hankel rank characterization of rational power series, Borcherds/Euler product Möbius transform, partition Turán log-concavity | Kronecker (1881); Stieltjes (1894); DeSalvo–Pak (2015) | Structural engine & Law-3 refutation ingredient (`Part 2`) |

**Honest `N1` Contribution Boundary:** What is genuinely `N1` here is (a) the explicit Law-3 counterexample refutation of naive additive-Hankel separation for modular vs. partial/mock thetas, (b) the unified zero-float 4-tier coordinate-free matrix-minor pipeline (`SF-01 #19`) pairing Euler–Witt Hankel saturation/collapse, 4th-moment `R_{H4}` zero-pole separation, and the column-space Rank–Crank Schur complement $S_{\mathrm{shadow}}(p, r)$ (verified against `CS-11` null-shuffled & shadow-doubled controls), and (c) the empirical commit-pinned 3-lab `aletheia v1.2.0 --lean-audit` forensic comparison.

---

## 2. Part 1 & Part 2 Results: Mock Thetas & 4-Tier Exact Filtration

### 2.1 Law-3 Refutation of Naive Additive-Hankel Separation
- **Counterexample 1 (Modular vs. Partial Theta):** $\vartheta_3(q) = 2\Theta_+(q) - 1$ implies $H_{12}^{(1)}(\vartheta_3) \equiv 2\,H_{12}^{(1)}(\Theta_+)$ entry-by-entry (`ratio == 2` verified over $\mathbb{Q}$). Both also have identical unshifted additive Hankel inertia `[7, 0, 5]` at $m=12$.
- **Counterexample 2 (Positive Modular $\eta$-Quotient Indefiniteness):** For $1/\eta(q) = \sum p(n)q^n$, $\det H_2^{(s)}(p) = p(s)p(s+2) - p(s+1)^2 < 0$ for every $s \in [25, 67]$ (`turan_neg_all = True`), forcing $n_-(H_m(p)) > 0$ (e.g. `[7, 0, 5]` at $m=12$).

### 2.2 Tier 1 (Additive $H_{12}(A)$) vs. Tier 2 (Euler–Witt $H_{10}(b) \to H_{14}(b)$) Summary

| Series | Class | Additive $H_{12}(A)$ Inertia | Euler–Witt Rank $H_{10} \to H_{14}$ | Exact Period ($\le 42$) | First 6 Euler–Witt Exponents $b_1..b_6$ |
|---|---|---:|---:|---:|---|
| `rational_fib` | `rational` | `(2, 10, 0)` | `10 -> 14` | `None` | `1, 1, 1, 1, 2, 2` |
| `eta1` | `modular_eta_quot` | `(6, 0, 6)` | **`1 -> 1`** | `1` | `-1, -1, -1, -1, -1, -1` |
| `p_ser_1_over_eta` | `modular_eta_quot` | `(7, 0, 5)` | **`1 -> 1`** | `1` | `1, 1, 1, 1, 1, 1` |
| `delta_q_tau` | `modular_eta_quot` | `(6, 0, 6)` | **`1 -> 1`** | `1` | `-24, -24, -24, -24, -24, -24` |
| `theta4` | `modular_eta_quot` | `(7, 0, 5)` | **`2 -> 2`** | `2` | `-2, -1, -2, -1, -2, -1` |
| `crank_neg1` | `modular_eta_quot` | `(6, 0, 6)` | **`2 -> 2`** | `2` | `-3, -1, -3, -1, -3, -1` |
| `theta3` | `modular_eta_quot` | `(7, 0, 5)` | **`3 -> 3`** | `4` | `2, -3, 2, -1, 2, -3` |
| `partial_theta` | `partial_theta` | `(7, 0, 5)` | `10 -> 14` | `None` | `1, -1, 0, 1, -1, 1` |
| `false_pent` | `false_theta` | `(7, 0, 5)` | `10 -> 14` | `None` | `1, -2, 1, -1, 1, -2` |
| `m3_f` ($= R(-1; q)$) | `mock_order3` | `(7, 0, 5)` | `10 -> 14` | `None` | `1, -3, 5, -9, 21, -49` |
| `m3_cancel_f_plus_4psi_neg` | `mock_shadow_cancelled` | `(6, 0, 6)` | **`2 -> 2`** | `2` | `-3, -1, -3, -1, -3, -1` |
| `m3_double_f_minus_4psi_neg` | `mock_shadow_doubled` | `(6, 0, 6)` | `10 -> 14` | `None` | `5, -21, 77, -361, 1837, -9537` |
| `m3_cancel_nu_plus_q_om_q2` | `mock_shadow_cancelled` | `(6, 0, 6)` | **`4 -> 4`** | `4` | `0, 2, 0, -1, 0, 2` |
| `m3_double_nu_minus_q_om_q2` | `mock_shadow_doubled` | `(6, 0, 6)` | `10 -> 14` | `None` | `-2, 1, -2, -4, -8, -11` |
| `m3_cancel_2rho_plus_omega` | `mock_shadow_cancelled` | `(7, 0, 5)` | **`4 -> 4`** | `6` | `0, 1, 2, 1, 0, -1` |
| `m3_cancel_4chi_minus_f` | `mock_shadow_cancelled` | `(7, 0, 5)` | **`5 -> 5`** | `6` | `1, 1, -3, 1, 1, -1` |
| `m5_cancel_f0_plus_2psi0_neg` | `mock_shadow_cancelled` | `(6, 0, 6)` | **`6 -> 6`** | `10` | `-1, -1, -2, 0, -2, 0` |
| `m5_cancel_2psi1_neg_minus_f1` | `mock_shadow_cancelled` | `(6, 0, 6)` | **`6 -> 6`** | `10` | `-2, 0, -1, -1, -2, -1` |
| `m5_cancel_phi0_neg_q2_plus_psi0` | `mock_shadow_cancelled` | `(6, 0, 6)` | **`20` at $m=22$** | `20` | `1, -2, 2, 0, 2, -2` |
| `m5_double_phi0_neg_q2_minus_psi0` | `mock_shadow_doubled` | `(6, 0, 6)` | `22` at $m=22$ | `None` | `-1, -1, -2, -2, -4, -6` |
| `cs11_shuf_eta1 / theta3 / crank` | `cs11_null_shuffled` | `(6..7, 0, 5..6)` | non-saturating (`> orig`) | `None` | erratic explosive integers |

*(Note: Testing the rank trajectory $H_{10} \to H_{14}$ avoids false saturation from accidental single-dimension Padé singularities such as `m3_chi` and `m3_rho` having $\det H_{12}(b) = 0$ while jumping back to full rank `14` at $m=14$.)*

### 2.3 Tier 3: Log-Derivative $H_8(c)^2$ Exact `R_opt` vs. `R_{H4}` (`CS-11` Unmasking)

| Series | Class | `R_opt` ($\times 10^4$ floor) | $\lceil R_{\mathrm{opt}} \rceil$ | `R_{H4}` ($\times 10^4$ floor) | $\lceil R_{H4} \rceil$ |
|---|---|---:|---:|---:|---:|
| `E4` | `modular_interior_zero` | `10000` | `2` | **`20000`** | **`3`** |
| `E6` | `modular_interior_zero` | `10000` | `2` | **`20000`** | **`3`** |
| `E2` | `quasimodular` | `10000` | `2` | **`20000`** | **`3`** |
| `m3_f` | `mock_order3` | `10000` | `2` | **`30538`** | **`4`** |
| `m5_f0` | `mock_order5` | `10000` | `2` | **`34619`** | **`4`** |
| `false_pent` | `false_theta` | `10006` | `2` | **`42798`** | **`5`** |
| `partial_theta` | `partial_theta` | `20619` | `3` | **`52660`** | **`6`** |

In addition, $E_2, E_4, E_6$ satisfy Ramanujan's exact ODE closure ($12 D(E_2) = E_2^2 - E_4$, $3 D(E_4) = E_2 E_4 - E_6$, $2 D(E_6) = E_2 E_6 - E_4^2$) to $O(q^{70})$ with `0` residual, and $\Delta(q)$ satisfies exact Hecke–Gram Schur complement $S(\Delta, T_{p,12}\Delta) = 0$ for $p \in \{2, 3, 5\}$.

---

## 3. Part 3 Results: Rank–Crank Column-Space Schur Complement $S_{\mathrm{shadow}}(p, r)$

| Prime $p$ | Genus $g(X_0(p))$ | Crank $\operatorname{rank}(A)$ by $r = 0..p-1$ | Rank $\operatorname{rank}(B)$ by $r = 0..p-1$ | $S_{\mathrm{shadow}}(p, r)$ Rank by $r = 0..p-1$ | Legendre $\left(\frac{1-24r}{p}\right)$ |
|---:|---:|---|---|---|---|
| **`5`** | `0` | `[1, 1, 1, 1, 0]` | `[2, 1, 1, 2, 0]` | **`[1, 0, 0, 1, 0]`** | `[+1, -1, -1, +1, 0]` (**exact match!**) |
| **`7`** | `0` | `[1, 1, 1, 1, 1, 0, 1]` | `[2, 1, 2, 1, 1, 0, 2]` | **`[1, 0, 1, 0, 0, 0, 1]`** | `[+1, -1, +1, -1, -1, 0, +1]` (**exact match!**) |
| **`11`** | **`1`** | `[1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1]` | `[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]` | **`[5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]`** | Genus-1 + mock full-rank explosion |
| **`13`** | `0` (no cong.) | `[6]*13` | `[6]*13` | **`[6]*13`** | Garvan rank-1 crank collapse terminates |

- **Exact 7th-Order Hickerson Matches (`22` terms, `0` residual on the exact 3 QR classes):**
  - `7k+0`: $N(0,7;7k) - N(2,7;7k) \equiv [q^k]\mathcal{F}_0(q)$
  - `7k+2`: $N(1,7;7k+2) - N(2,7;7k+2) \equiv [q^k]\mathcal{F}_2(q)$
  - `7k+6`: $2 N(2,7;7k+6) - N(1,7;7k+6) - N(0,7;7k+6) \equiv [q^{k+1}]\mathcal{F}_1(q)$
- **Mod-11 Congruence Class `11k+6` Blind-Kernel Certificate:**
  - Parseval equidistribution defect $\mathcal{D}_{\mathrm{crank}}(11; 11k+6) \equiv 0$, while $\mathcal{D}_{\mathrm{rank}}(11; 11k+6) = 44, 286, 2618, 17182, 91696, 420266, 1721302, 6413968, \dots > 0$.
  - $S_{\mathrm{shadow}}(11, 6) \in \mathbb{Z}^{5\times 5}$ is **strictly positive definite** (`inertia = (5, 0, 0)`, all 5 leading Bareiss principal minors strictly positive with bit-lengths `[22, 37, 44, 48, 50]`).
  - `R_opt` = `1.0000+` (`ceil = 2`), **`R_{H4}` = `2.0274+` (`ceil = 3`)** (strictly surpassing `R_opt` by `+1.027` from trace moments alone!), verified `0`-residual invariant under exact $O(5, \mathbb{Q})$ Householder orthogonal conjugations (both built-in and unseen in `test_r5_ramanujan_mock_shadows.py`).

---

## 4. Part 4 Results: BigInt $\tau(n)$, Cubic Theta AGM & 3-Lab `aletheia v1.2.0` Lean 4 Forensics

### 4.1 Exact $\tau(n)$ (`n = 1..500`, `95` primes) & Borwein Cubic Theta AGM ($O(q^{100})$)
- **Congruences:** `mod 691` ($\sigma_{11}$), Kolberg `mod 2048` (all odd $n$: multipliers `{1:1, 3:1217, 5:1537, 7:705}`), Swinnerton-Dyer `mod 729` ($n^{135}\sigma_{227}$, $3\nmid n$), Swinnerton-Dyer `mod 125` ($n^{41}\sigma_{29}$, $5\nmid n$), `mod 7` ($n\sigma_3$), Wilton `mod 23` (inert primes $\equiv 0$, split primes $\in \{2, -1\}$) — **all 7 exact (`True`)**.
- **Hecke & Deligne & Lehmer:** `1,143` coprime pairs $\tau(mn)=\tau(m)\tau(n)$, `19` prime-power recursions, integer Deligne bound $\tau(p)^2 \le 4 p^{11}$ (`max` exact Sato–Tate ratio at $p=103$: `12741344527718757576976/13842338707244455781047` $\approx 0.9204$), and $\tau(n) \neq 0$ for all $1 \le n \le 500$.
- **Cubic Theta AGM ($O(q^{100})$):** $b_{\mathrm{lat}} \equiv b_{\mathrm{prod}}$, $c^3_{\mathrm{lat}} \equiv c^3_{\mathrm{prod}}$, $a(q)^3 \equiv b(q)^3 + c(q)^3$, $3 a(q^3) \equiv a(q) + 2 b(q)$, and $3 b(q^3)^3 \equiv b(q)(a^2 + ab + b^2)$ all exact; Euler–Witt Hankel ranks `3` for `b(q)` (`[-3,-3,-2]`) and `2` for `\tilde{c}(q)/3` (zero-mean `[1,1,-2]`).

### 4.2 Commit-Pinned 3-Lab Live `aletheia v1.2.0 --lean-audit` Forensics (`20` Files)

| Read-Only Lab Repo & Pinned Commit | Audited Files | `aletheia v1.2.0` Findings | Key Forensic Observation |
|---|---:|---|---|
| `dm-math-formal-conjectures@d8d031d4` | `3` | `public import` on all 3; `sorry`: `RamanujanTau.lean` (`3`: `L60, L66, L71`), `PartitionParity.lean` (`16`), `Gourevitch.lean` (`1`: `L43`) | Even the unit-test lemma `@[category test] lemma τ_two : τ 2 = -24 := by sorry` (`L60`) is unfinished; `ramanujan_petersson` uses real `(p : ℝ)^(11/2)` rather than pure-integer `τ(p)^2 ≤ 4 * p^11`. |
| `openai-math@4eaee875` | `15` | **`15/15` `mathlib_clean: true`** (`0` `sorry`s, `0` axioms, `0` trust escapes) | Clean end-to-end formalization of metaplectic Eisenstein-ring Ramanujan sums (`CubicThetaRamanujan*.lean`), Egyptian-fraction finite-ring CRT character sums, and Ostmann/JointDickman Ramanujan kernels. |
| `anthropics-flt@6e837e75` | `2` | **`2/2` `mathlib_clean: true`** (`0` `sorry`s, `0` trust escapes) | Proves Ramanujan's exact integer Eisenstein ODE system `12 D(P)=P^2-Q`, `3 D(Q)=PQ-R`, `2 D(R)=PR-Q^2` (`Thm_` + `S_EisensteinSeries_ramanujan_system_qExpansion_int.lean`). |

---

## 5. Exact Reproduction Commands (4-Mode Isolated `-I` R4 + `aletheia audit-check`)

```bash
# 1. 4-Mode isolated R4 bit-identical parity on main probe & R5 suite
for f in "-I -B" "-I -O -B" "-I -B -W error" "-I -O -B -W error"; do
  python3 $f ramanujan_mock_shadows.py | sha256sum
  python3 $f test_r5_ramanujan_mock_shadows.py | sha256sum
done

# 2. aletheia v1.2.0 self-hygiene & R4 audit-check
PYTHONPATH=../../../publish/aletheia python3 -B -W error -m aletheia audit-check . \
  --scripts ramanujan_mock_shadows.py test_r5_ramanujan_mock_shadows.py --json
```
