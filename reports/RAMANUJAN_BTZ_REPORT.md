# Wave 2 Round 4 — Arm R4-1 (`AUDIT-044`): Zero-Float Ramanujan-Graph Certifier, $H^1(G, \mathbb{Z}_2)$ $p$-adic BTZ Wormhole Holonomy, and the 24 Niemeier Companions of $\Lambda_{24}$

- **Arm / Owner:** Arm R4-1 (`fractals-probe`), Round 4 Portal `R4-P01` & `R4-P06 (#18)`
- **Oracle Class:** `exact` (Parts A, B1, B2, D, and Part C theta/ball-count theorems — `0` floats, pure `int`/`Fraction`) + `exact+sampled` (Part C Monte Carlo Voronoi $G$ & 400-block `siliquant#24` benchmark, seeded `default_rng(20260401)`)
- **Honest Law-4 Novelty Tag:** **`N1`** (clean-room zero-float executable cross-domain unification of `SF-01` Schur/Bunch–Kaufman inertia, `SF-03` Bruhat–Tits $p$-adic BTZ quotients, `SF-05` $H^1(G,\mathbb{Z}_2)$ holonomy cohomology, and `SF-06` 24 Niemeier / $\Lambda_{24}$ lattices — with zero inflated `N2` claim and strict quarantine of all classical `N0` theorems below)
- **Read-Only External Anchors (Zero External Writes):**
  - `anthropics/flt@6e837e75355538c7f80bab5b956861e86c4eacc2`:
    - `Definitions/Def_CerednikDrinfeld_HeckeTower.lean:23-24` (`arrowDegree N α = if ℓ ∣ N then ℓ else ℓ + 1`, Bruhat–Tits $p$-adic Shimura quotient degree $p+1$)
    - `Definitions/Def_AutomorphicForm_HeckeEigensystem.lean:24-29` (`def twist Φ χ`, character twisting of Hecke operators)
  - `Moissanite-Labs/siliquant#24` (`AUDIT-028`, `AUDIT-031`, `AUDIT-035`) and `AUDIT-042` (`padic_btz_leech_holography.py`)
- **Artifacts (`symbiosis/round4/ramanujan-btz-graphs/`):**
  - `ramanujan_btz_graphs.py` — self-contained certifier & verifier (`1096` lines, zero bare `assert`s)
  - `ramanujan_btz_graphs_certificate.json` — canonical certificate (`canonical_sha256 = 88edebc4ee95ea77ac4557314d7cde655d27fe52fb162eb7396d8cb4f9d7f143`, file `sha256 = 6e1349cb679ffda44162135bbeac536c5603339f061fdd93a95086631446268c`)
  - `RAMANUJAN_BTZ_REPORT.md` — this report

---

## 1. Strict Law-4 `N0` Prior-Art Quarantine Table

Every classical theorem below is explicitly quarantined as **`N0`** (consistent with `RAMANUJAN_PORTALS_R4.md` `R4-N0-01..17`) and used strictly as a verified mathematical foundation rather than claimed as a discovery:

| Quarantine ID | Classical Result / Object | Primary Prior Art | Role in `AUDIT-044` |
|---|---|---|---|
| `R4-N0-01` | $\Delta(q) = q\prod_{n\ge 1}(1-q^n)^{24}$, $\tau(n)$ multiplicativity, $|\tau(p)| \le 2p^{11/2}$ | Ramanujan (1916); Mordell (1917); Hecke (1937); Deligne (1974) | Exact integer $q$-expansion backbone of Part C |
| `R4-N0-05` | Classification of the 24 even unimodular 24D lattices, $\Theta_N(q) = E_4^3 + (r_N - 720)\Delta$, Milnor's isospectral pair ($D_{16}^+ \oplus E_8$ vs $E_8^3$), Umbral Moonshine | Milnor (1964); Niemeier (1973); Conway–Sloane (*SPLAG* Ch. 16); Cheng–Duncan–Harvey (2014) | Exact theta baseline for Part C quantization comparison |
| `R4-N0-06` | Ramanujan graphs ($\max_{\lambda\neq\pm d}|\lambda| \le 2\sqrt{d-1}$), LPS / Margulis Bruhat–Tits quotients, Alon–Boppana bound | Lubotzky–Phillips–Sarnak (1988); Margulis (1988); Alon–Boppana (1991) | Spectral definition certified via exact integer inertia in Part A |
| `R4-N0-07` | Signed 2-lifts $(G,\sigma)$ and existence of Ramanujan 2-lifts via interlacing polynomials | Bilu–Linial (2006); Marcus–Spielman–Srivastava (2015) | Exact $H^1(G,\mathbb{Z}_2)$ cohomology sweep in Part B1 |
| `R4-N0-08` | Signed Laplacian $L^\chi$ is invertible ($\ker L^\chi = 0$, $+1$ rank jump) iff $(G,\chi)$ is unbalanced | Harary (1953); Zaslavsky (1982); Haynsworth (1968) | Classical root of single-mouth DtN rank jump (Part B2) |
| `R4-N0-09..10` | Bundle Laplacian $\det(\Delta^\Phi)$ (CRSFs) and electrical DtN / $\Delta$-Y equivalence | Kenyon (2011); Curtis–Ingerman–Morrow (1998) | Classical foundation for signed boundary DtN maps |
| `R4-N0-EXT` | Symmetric matrix Sylvester inertia via $1\times 1$/$2\times 2$ block $LDL^\top$ & exact rational characteristic polynomial | Sylvester (1852); Bunch–Kaufman (1977); Faddeev–LeVerrier (1840/1949) | Zero-float certification engine in Parts A & B |

**What IS genuinely synthesized here (`N1`, falsifiable, pure-$\mathbb{Q}/\mathbb{Z}$):**
1. **Zero-Float Exact Integer Ramanujan Certifier & Witness Generator (Part A):** Certifies $4p\,I - A_\perp^2 \succeq 0$ (unsigned) and $4p\,I - A_\chi^2 \succeq 0$ (signed 2-lifts) with **zero floating-point arithmetic** via exact rational Bunch–Kaufman block $LDL^\top$, producing explicit integer refutation vectors $w \in \mathbb{Z}^n$ with $w^\top M w < 0$ whenever $n_- > 0$.
2. **Exhaustive $H^1(G, \mathbb{Z}_2)$ Census Across 9 Regular Graphs (`840` Cohomology Classes, Part B1):** Proves nontrivial holonomy $[\chi] \notin \{[+1], [-1]\}$ is universally **necessary** (`100%`) yet **not sufficient** (`Heawood H_14` `21` nontrivial fails; `Octahedron K_{2,2,2}` `24` nontrivial fails, each with an integer witness), AND exhibits a **non-Ramanujan 3-regular base graph** (`Dumbbell14`, base $n_-=1$, $w^\top M w = -957{,}270{,}381{,}116 < 0$) whose $H^1$ cohomology still yields **`196/256` (`49/64`) strictly Ramanujan signed 2-lifts**.
3. **2-Mouth $p$-adic BTZ Wormhole Parity Bifurcation & Balanced Krein Signature Law (Part B2 — `R4-P06 #18` Bridge):**
   - **Odd vs. Even Horizon Parity Bifurcation:** On odd-horizon 2-mouth wormholes (`p=2, L1=L2=3, D=1`), twisting BOTH mouths `(--)` mirrors the untwisted spectrum ($\chi_{--}(x) = \chi_{++}(-x)$, failing $|\lambda| \le \sqrt{5}$), whereas asymmetric 1-twist `(-+)` strictly compresses the bulk to $|\lambda| \le \sqrt{5}$ (`inertia(5I - A^2) = [4, 2, 0]`). On even-horizon bipartite wormholes (`p=2, L1=L2=4, D=1`), twisting BOTH mouths `(--)` **uniquely** compresses the bulk to $|\lambda| \le 2$ (`inertia(4I - A^2) = [6, 2, 0]`) while both `(++)` and `(-+)` exceed `2` (`[6, 0, 2]`).
   - **Exact Balanced Krein Signature Law (Direct Bridge to `@gravity-probe` / `R4-P04`):** Across all `8` tested single-mouth ($k=1$) and 2-mouth ($k \in \{1,2\}$) twisted BTZ configurations with boundary/collar trivialization ($F \subset E(I)$), the boundary Observer Difference Operator $\Delta\Lambda_\partial(\chi) := \Lambda_\partial(\chi) - \Lambda_\partial(1)$ satisfies
     $$\operatorname{inertia}\!\big(\Delta\Lambda_\partial(\chi)\big) \;=\; \big(k,\; |B| - 2k,\; k\big)$$
     paired with strictly positive monopole unmasking $\Phi_\partial(\chi) = \mathbf{1}_B^\top \Lambda_\partial(\chi)\mathbf{1}_B > 0$ — realizing the rank-2 Krein flip mechanism $w_e[(e_u+e_v)^{\otimes 2} - (e_u-e_v)^{\otimes 2}]$ in exact rational arithmetic.
4. **All 24 Niemeier Companions of $\Lambda_{24}$: Universal Ball-Cap Invariance & Non-Monotonic Quantization Split (Part C):** Proves $|B_N(m)| - |B_{\Lambda_{24}}(m)| = 24 h_N \sum_{k=1}^m \tau(k)$ identically across all 24 Niemeier lattices ($m = 1..214$), proves universal ball-cap invariance (`m_cap = 2, 6, 13, 26, 53, 214` at `1.0..4.0 bpw`), and demonstrates via exact nearest-point decoders that Milnor's isospectral twin $D_{16}^+ \oplus E_8$ beats $E_8^3$ in unbiased Voronoi $G$ despite identical $\Theta \equiv E_4^3$ and identical $\rho^2 = 3$, while max-root $D_{24}^+$ (`r=1104`) degrades $G$, and rootless $\Lambda_{24}$ ($\rho^2 = 2$) dominates all 23 root-bearing companions.

---

## 2. Parts A & B1 — Zero-Float Ramanujan Certifier & Exhaustive $H^1(G, \mathbb{Z}_2)$ Census (`840` Classes)

For any connected $d$-regular graph $G$ ($p := d - 1$) on $n$ vertices, eliminating the trivial eigenspace(s) yields an **exact integer** symmetric matrix whose positive semidefiniteness is equivalent to the Ramanujan bound $\max_{\lambda \neq \pm d} |\lambda| \le 2\sqrt{p}$:
- **Non-bipartite:** $N_{\mathrm{Ram}}(G) := 4p\,n I - n A^2 + d^2 J \succeq 0$.
- **Bipartite ($|L|=|R|=n/2$):** $N_{\mathrm{Ram}}^{\mathrm{bip}}(G) := 2p\,n I - \frac{n}{2} A^2 + d^2 (J_{LL} + J_{RR}) \succeq 0$.
- **$\mathbb{Z}_2$-signed 2-lift $(G,\chi)$:** $R_G(\chi) := 4p\,I - A_\chi^2 \succeq 0$ (no trivial projection needed, since new-spectrum eigenvalues of the 2-lift are precisely $\operatorname{Spec}(A_\chi)$).

Exact rational Bunch–Kaufman pivoting ($1\times 1$ and $2\times 2$ pivots) computes Sylvester inertia $(n_+, n_0, n_-)$ with **zero floats**; whenever $n_- > 0$, back-substitution on the negative block yields a primitive integer vector $w \in \mathbb{Z}^n$ verified directly via $w^\top M w < 0$. Vertex-switching gauge invariance ($A_{S\chi S} = S A_\chi S$) is explicitly verified on every graph.

| Graph | $(n, d, p)$ | Bip? | Base Ram? (`inertia`) | $\beta_1$ | $|H^1|$ | Ram Lifts (Fraction) | `n_-` Histogram | Nontrivial Fails | Sample Integer Witness $w^\top M w$ |
|---|---|---|---|---:|---:|---:|---|---:|---:|
| `K4` | `(4, 3, 2)` | No | Yes (`[4,0,0]`) | 3 | 8 | `6/8` (`3/4`) | `{0:6, 1:2}` | 0 | — |
| `K3_3_bipartite` | `(6, 3, 2)` | Yes | Yes (`[6,0,0]`) | 4 | 16 | `15/16` | `{0:15, 2:1}` | 0 | — |
| `Prism_Y3_2mouth` | `(6, 3, 2)` | No | Yes (`[6,0,0]`) | 4 | 16 | `14/16` (`7/8`) | `{0:14, 1:2}` | 0 | — |
| `Cube_Q3_bipartite` | `(8, 3, 2)` | Yes | Yes (`[8,0,0]`) | 5 | 32 | `31/32` | `{0:31, 2:1}` | 0 | — |
| `Petersen_P10` | `(10, 3, 2)` | No | Yes (`[10,0,0]`) | 6 | 64 | `62/64` (`31/32`) | `{0:62, 1:2}` | 0 | — |
| `Heawood_H14_bipartite` | `(14, 3, 2)` | Yes | Yes (`[14,0,0]`) | 8 | 256 | `234/256` (`117/128`) | `{0:234, 2:22}` | **21** | `-36` (`mask=1`, `n_-=2`) |
| `K5` | `(5, 4, 3)` | No | Yes (`[5,0,0]`) | 6 | 64 | `62/64` (`31/32`) | `{0:62, 1:2}` | 0 | — |
| `Octahedron_K222` | `(6, 4, 3)` | No | Yes (`[6,0,0]`) | 7 | 128 | `102/128` (`51/64`) | `{0:102, 1:26}` | **24** | `-84` (`mask=1`, `n_-=1`) |
| `Dumbbell14_nonRam_base` | `(14, 3, 2)` | No | **No** (`[13,0,1]`) | 8 | 256 | **`196/256` (`49/64`)** | `{0:196, 1:56, 2:4}` | 58 | Base: `-957270381116`; Lift `mask=1`: `-19149241839` |
| **Total** | **9 graphs** | — | **8 Ram / 1 Non-Ram** | — | **840** | — | — | — | **100% Zero-Float Certified** |

**Key Structural Consequences:**
- **Universal Necessity (`100%`):** Both the trivial class `[+1]` (spectral radius $d > 2\sqrt{d-1}$) and the antibalanced class `[-1]` (coinciding with `[+1]` iff $G$ is bipartite) ALWAYS fail $4p\,I - A_\chi^2 \succeq 0$.
- **Strict Non-Sufficiency:** On `Heawood_H14_bipartite` (`21` nontrivial failing classes, e.g., `mask=1`, $w=[6,7,3,6,7,7,6,0,\dots,0]$, $w^\top(8I - A_\chi^2)w = -36$) and `Octahedron_K222` (`24` nontrivial failing classes, e.g., `mask=1`, $w=[9,6,9,6,8,7]$, $w^\top(12I - A_\chi^2)w = -84$), nontrivial holonomy alone does not guarantee Ramanujan 2-lift expansion.
- **Bipartite Duality & Non-Ramanujan Lift Recovery:** On any bipartite $(p+1)$-regular graph, $A_\chi$ has symmetric spectrum $\pm\lambda$, so $4p\,I - A_\chi^2 \succeq 0$ is algebraically equivalent to Harary's signed-Laplacian spectral floor $\lambda_{\min}(L^\chi) \ge (\sqrt{p}-1)^2$. Meanwhile, `Dumbbell14` (two 7-vertex 3-regular-minus-1-stub lobes joined by a single cut-bridge `(6,13)`) fails base Ramanujan (`n_-=1`, $w^\top M w = -957{,}270{,}381{,}116 < 0$), yet **`196/256` (`76.5625%`)** of its $\mathbb{Z}_2$ 2-lift new spectra are strictly Ramanujan!
- **Cross-Arm Hook (`R4-P05`, `@peer-weaver`):** The Bareiss-certified sparse 3-regular graphs (`Petersen_P10`, `Heawood_H14_bipartite`, and their certified Ramanujan signed 2-lifts) provide zero-float sparse expander mixer templates directly comparable against dense Hadamard $H_{96}$ (`AUDIT-035`/`039`).

---

## 3. Part B2 — $p$-adic BTZ Quotients: Horizon-Parity Bifurcation & Balanced Krein Signature Law (`SF-01 #18`)

All boundary Dirichlet-to-Neumann (DtN) Schur complements $\Lambda_\partial(\chi) = L_{BB} - L_{BI}(L^\chi_{II})^{-1} L_{IB}$, traces, monopole fluxes $\Phi_\partial(\chi) := \mathbf{1}_B^\top \Lambda_\partial(\chi)\mathbf{1}_B$, Krein difference inertias $\operatorname{inertia}(\Lambda_\partial(\chi) - \Lambda_\partial(1))$, and bulk characteristic polynomials $\det(xI - A^\chi_{II}) \in \mathbb{Z}[x]$ are computed in **100% pure `Fraction`/`int` arithmetic**.

### 3.1 Single-Mouth $p$-adic BTZ Quotients ($\beta_1 = 1$, $D = 1$)
| $(p, L)$ | $|B|$ | Untwisted `(rank, Tr)` | Twisted `(rank, Tr)` | Monopole Flux $\Phi_\partial(\chi)$ | $\operatorname{inertia}(\Delta\Lambda_\partial(\chi))$ | Bulk $4pI - A_{II}^2 \succeq 0$? |
|---|---:|---|---|---:|---|---|
| `(2, 3)` | 3 | `(2, 3/2)` | `(3, 9/5)` | `8/5` | **`(1, 1, 1)`** | Yes |
| `(2, 4)` | 4 | `(3, 32/15)` | `(4, 16/7)` | `12/7` | **`(1, 2, 1)`** | Yes |
| `(2, 5)` | 5 | `(4, 30/11)` | `(5, 14/5)` | `44/25` | **`(1, 3, 1)`** | Yes |
| `(3, 4)` | 8 | `(7, 17/3)` | `(8, 40/7)` | `16/7` | **`(1, 6, 1)`** | Yes |

### 3.2 Two-Mouth $p$-adic BTZ Wormholes ($\beta_1 = 2$, $H^1 = \mathbb{Z}_2^2$) — Odd vs. Even Horizon Parity Bifurcation
| Wormhole Geometry | Holonomy Config | DtN Rank | DtN Trace | $\Phi_\partial(\chi)$ | $\operatorname{inertia}(\Delta\Lambda_\partial)$ | Bulk Characteristic Polynomial $\chi(x)$ | Sharp Threshold Inertia |
|---|---|---:|---:|---:|---|---|---|
| **Odd $L_1=L_2=3$** (`p=2, |B|=4`, $|I|=6$) | `(+,+), bridge+` | 3 | `11/6` | `0/1` | — | $x^6 - 7x^4 - 4x^3 + 11x^2 + 12x + 3$ | $5I-A^2$: `[5,0,1]` (Fail) |
| **Odd $L_1=L_2=3$** | `(+,+), bridge-` | 3 | `11/6` | `4/3` (*) | — | $x^6 - 7x^4 - 4x^3 + 11x^2 + 12x + 3$ | $5I-A^2$: `[5,0,1]` (Fail) |
| **Odd $L_1=L_2=3$** | `(-,+), bridge+` | 4 | **`17/8`** | `11/8` | **`(1, 2, 1)`** | $x^6 - 7x^4 + 11x^2 - 5$ | $5I-A^2$: **`[4,2,0]` (PASS!)** |
| **Odd $L_1=L_2=3$** | `(-,-), bridge+` | 4 | **`50/21`** | `2/1` | **`(2, 0, 2)`** | $x^6 - 7x^4 + 4x^3 + 11x^2 - 12x + 3$ | $5I-A^2$: `[5,0,1]` (Fail) |
| **Even $L_1=L_2=4$** (`p=2, |B|=6`, $|I|=8$) | `(+,+)` | 5 | `37/12` | `0/1` | — | $x^8 - 9x^6 + 20x^4 - 4x^2$ | $4I-A^2$: `[6,0,2]` (Fail) |
| **Even $L_1=L_2=4$** | `(-,+)` | 6 | **`68/21`** | `32/21` | **`(1, 4, 1)`** | $x^8 - 9x^6 + 24x^4 - 20x^2$ | $4I-A^2$: `[6,0,2]` (Fail) |
| **Even $L_1=L_2=4$** | `(-,-)` | 6 | **`237/70`** | `16/7` | **`(2, 2, 2)`** | $x^8 - 9x^6 + 28x^4 - 36x^2 + 16$ | $4I-A^2$: **`[6,2,0]` (PASS!)** |

`(*)` **Exact Gauge Subtlety Verified:** Flipping the cut-bridge `(0,3)` is a pure vertex gauge transformation ($S = \operatorname{diag}(+1,+1,+1,-1,-1,-1,+1,+1,-1,-1)$): it preserves `dtn_rank = 3`, `dtn_trace = 11/6`, and `bulk_charpoly_int` identically, while rotating $\ker\Lambda_\partial$ from $\mathbf{1}_B$ to $(+1,+1,-1,-1)^\top$ (hence $\mathbf{1}_B^\top \Lambda_\partial \mathbf{1}_B = 4/3 \neq 0$ unless the boundary/collar gauge is fixed, matching `R4-P04`'s explicit hypothesis $F \subset E(I)$!).

**Three Verified Structural Laws in Part B2:**
1. **Strict Boundary Holographic Stratification:** Boundary DtN trace strictly orders the number of twisted horizon mouths on both wormholes: `11/6 < 17/8 < 50/21` (odd $L=3,3$) and `37/12 < 68/21 < 237/70` (even $L=4,4$), even though `dtn_rank` saturates at $|B|$ once $k \ge 1$.
2. **Odd-vs-Even Horizon Parity Bifurcation:**
   - **Odd horizons ($L=3,3$):** Twisting BOTH odd horizons satisfies exact anti-holonomy symmetry $\chi_{--}(x) = (-1)^6 \chi_{++}(-x)$, restoring the untwisted spectral radius ($\lambda_{\max} > \sqrt{5}$, refutation witness `[-7,-5,5,3,4,0]`). Only the **asymmetric 1-twist** `(-,+)` (equivalently `(+,-)`) breaks the symmetric/antisymmetric resonance and strictly compresses the bulk to $|\lambda| \le \sqrt{5}$ (`[4, 2, 0]`).
   - **Even bipartite horizons ($L=4,4$):** Because the bulk is bipartite, $\chi(x)$ is already even in $x$; twisting BOTH mouths `(--)` strictly compresses the bulk to exact spectral radius $|\lambda| \le 2$ (`[6, 2, 0]`, with $4I - A_{--}^2$ positive semidefinite), whereas `(++)` and `(-+)` both fail (`[6, 0, 2]`).
3. **Balanced Krein Difference Signature (`SF-01 #18` Bridge to `@gravity-probe` / `Foundation-0/hawking`):** Across ALL `8` tested twisted configurations ($k \in \{1, 2\}$ twisted mouths, untwisted collar/bridge $F \subset E(I)$), $\operatorname{inertia}(\Lambda_\partial(\chi) - \Lambda_\partial(1)) = (k, |B|-2k, k)$ — exact $k$-for-$k$ balance between monopole/positive unmasking ($n_+ = k$) and multipolar negative Krein eigenvalues ($n_- = k$), directly validating the rank-2 Krein flip prediction of `R4-P04`!

---

## 4. Part C — All 24 Niemeier Companions of $\Lambda_{24}$: Exact $\tau(k)$ Oscillation & Quantization Split

### 4.1 Exact Integer Theta & Ball-Count Theorems (`0` Floats)
All `24` Niemeier even unimodular 24D lattices (`Leech_Lambda24` plus `23` ADE root-bearing companions) are verified to satisfy uniform Coxeter number $h_N$, root count $r_N = 24 h_N$, and exact modular decomposition $\Theta_N(q) = E_4(q)^3 + (r_N - 720)\Delta(q)$ through $m = 214$, yielding:
1. **Exact Five Isospectral Niemeier Pairs:** `(A5^4_D4, D4^6)` ($h=6$), `(A9^2_D6, D6^4)` ($h=10$), `(A11_D7_E6, E6^4)` ($h=12$), `(A17_E7, D10_E7^2)` ($h=18$), and Milnor's pair `(D16_E8, E8^3)` ($h=30$).
2. **Exact Ramanujan-$\tau$ Cumulative Ball-Count Identity (Verified $m = 1..214$ for all 24 lattices):**
   $$|B_N(m)| - |B_{\Lambda_{24}}(m)| \;=\; 24\,h_N \sum_{k=1}^{m} \tau(k) \;=:\; 24\,h_N\,T(m).$$
   Over $m = 1..214$, the cumulative cusp-form partial sum $T(m)$ oscillates with **`115` positive**, **`99` negative**, and **`0` zero** values (`T(1)=1`, `T(2)=-23`, `T(13)=-578358`, `T(53)=-2000920858`, `T(214)=1970276759459`).
3. **Universal Ball-Cap Invariance Across All 24 Niemeier Lattices:** Despite $|B_N(m)| - |B_{\Lambda_{24}}(m)|$ changing sign 99+ times, Deligne's $|\tau(p)| \le 2p^{11/2}$ keeps the cusp perturbation tiny compared to the $O(m^{12})$ Eisenstein growth $E_4^3$, so **ALL 24 Niemeier lattices share the exact same integer shell cap $m_{\mathrm{cap}}(b)$** across every tested `siliquant#24` bit rate:

| Bit Budget `b` (bpw) | `1.0` | `1.5` | `2.0` | `2.5` | `3.0` | `4.0` |
|---|---:|---:|---:|---:|---:|---:|
| Universal $m_{\mathrm{cap}}$ (ALL 24 Niemeier lattices) | `2` | `6` | `13` | `26` | `53` | `214` |

### 4.2 Exact-Decoder Quantization Split (`siliquant#24` Bridge, `oracle_class = exact+sampled`)
Using exact nearest-point decoders for even unimodular $D_{8k}^+$ (`E_8 = D_8^+`, `D_{16}^+`, `D_{24}^+`) with verified deep-hole covering radii $\rho^2(D_{16}^+ \oplus E_8) = 2 + 1 = 3$ and $\rho^2(D_{24}^+) = 3$ (vs. $\rho^2(\Lambda_{24}) = 2$, `AUDIT-028`), evaluated on `30,000` uniform `[0,2)^24` samples (unbiased Voronoi $G$) and `400 x 24` Gaussian safe-scale blocks (`default_rng(20260401)`):

| 24D Unimodular Lattice | Roots $r_N$ | Exact $\rho^2$ | Unbiased Voronoi $G$ (`30k` MC) | Gap $\frac{\rho^2}{24 G}$ (dB) | `2.0 bpw` Safe MSE / Proved Bound (dB) | `4.0 bpw` Safe MSE / Proved Bound (dB) |
|---|---:|---:|---:|---:|---|---|
| **$\Lambda_{24}$ (Leech)** | `0` | **`2`** | `0.065771` (`AUDIT-028` ref) | `1.028` | `—` / **`-8.318`** | `—` / **`-22.689`** |
| **$D_{16}^+ \oplus E_8$ (Milnor twin)** | `720` | `3` | **`0.071353`** | `2.435` | `-8.221` / `-5.774` (`0` out) | `-23.235` / `-20.784` (`0` out) |
| **$E_8^3$ (Isospectral twin)** | `720` | `3` | `0.071686` (exact `929/12960 = 0.071682`) | `2.415` | `-8.230` / `-5.774` (`0` out) | `-23.251` / `-20.784` (`0` out) |
| **$D_{24}^+$ (Max roots)** | `1104` | `3` | `0.072524` | `2.364` | `-8.142` / `-5.774` (`0` out) | `-23.148` / `-20.784` (`0` out) |

**Quantitative Conclusions (Law-4 Honest):**
- **Exact Isospectral Quantization Split:** Even with **identical theta series $\Theta \equiv E_4^3$** and **identical covering radius $\rho^2 = 3$**, Milnor's twin $D_{16}^+ \oplus E_8$ achieves strictly lower unbiased Voronoi $G$ (`0.071353 < 0.071686`, `+0.020 dB` granular advantage) than $E_8^3$, while max-root $D_{24}^+$ (`r = 1104`) is strictly **worse** (`0.072524`, `-0.050 dB` vs $E_8^3$). (On finite `400`-block spherical Gaussian samples, `E_8^3` and `D_{16}^+ \oplus E_8` sit within `0.016 dB` sampling variance while both clearly beat `D_{24}^+` by `~0.08–0.10 dB`.)
- **Rootless $\Lambda_{24}$ Safe-Scale Dominance:** Because $\rho^2(\Lambda_{24}) = 2 < 3$, rootless $\Lambda_{24}$ dominates all three $\rho^2 = 3$ Niemeier companions by **`+2.544 dB`** (`2.0 bpw`) and **`+1.905 dB`** (`4.0 bpw`) in exact worst-case proved bound — at `2.0 bpw`, $\Lambda_{24}$'s **worst-case proved bound** (`-8.318 dB`) beats even the **average empirical MSE** (`-8.230`, `-8.221`, `-8.142 dB`) of all three root-bearing Niemeier decoders!

---

## 5. R1–R5 Verification Receipts & Reproducibility

- **Part D (`8/8` Must-Fail R5 Controls Passed):** `C1` non-regular graph (`NOT_REGULAR`), `C2` non-Ramanujan `Dumbbell14` refuted with `n_-=1` & integer witness, `C3` trivial `+1` lift on `K4` refuted (`quad = -7`), `C4` invalid sign `chi=2` (`INVALID_SIGN`), `C5` asymmetric matrix (`NOT_SYMMETRIC`), `C6` non-uniform Coxeter fake Niemeier (`NON_UNIFORM_COXETER`), `C7` wrong total rank `E8^2` (`BAD_NIEMEIER_RANK`), `C8` `bool` rejected as exact `int` (`INVALID_TYPE`).
- **4-Mode Isolated R4 Bit-Identical Replay (`~2.0s` per run):**
  ```bash
  python3 -I -B ramanujan_btz_graphs.py --json | sha256sum
  python3 -I -O -B ramanujan_btz_graphs.py --json | sha256sum
  python3 -I -B -W error ramanujan_btz_graphs.py --json | sha256sum
  python3 -I -O -B -W error ramanujan_btz_graphs.py --json | sha256sum
  ```
  All four modes AND `ramanujan_btz_graphs_certificate.json` match identically:
  - File/stdout `sha256`: `6e1349cb679ffda44162135bbeac536c5603339f061fdd93a95086631446268c`
  - Certificate `canonical_sha256`: `88edebc4ee95ea77ac4557314d7cde655d27fe52fb162eb7396d8cb4f9d7f143`
- **`aletheia v1.2.0` Gate:** `PYTHONPATH=../../../publish/aletheia python3 -B -W error -m aletheia audit-check . --scripts ramanujan_btz_graphs.py --json` → `PASS` (`0` CRLF, `0` `__pycache__`, `0` local-path leaks, `0` bare `assert`s, `0` unseeded RNG, `1/1` isolated R4).

## 6. Falsification Criteria
`AUDIT-044` is falsified if:
1. Any of the `9` base certifier verdicts or `840` $H^1(G,\mathbb{Z}_2)$ lift inertias disagrees with an independent exact eigensolver / rational characteristic polynomial root count, or any emitted integer witness $w$ fails $w^\top M w < 0$;
2. Any of the `8` twisted single-/two-mouth BTZ configurations violates `dtn_rank` jump, trace stratification, odd-vs-even bulk parity bifurcation (`5I - A^2` vs `4I - A^2`), or balanced Krein signature `inertia(Lambda(chi) - Lambda(1)) == (k, |B|-2k, k)`;
3. Any of the `24` Niemeier lattices violates $|B_N(m)| - |B_{\Lambda_{24}}(m)| = 24 h_N T(m)$ or universal `m_cap` across `1.0..4.0 bpw`, or the unbiased ordering $G(D_{16}^+\oplus E_8) < G(E_8^3) < G(D_{24}^+)$ reverses on independent large-sample re-evaluation;
4. Any of the `8/8` R5 controls fails to reject, or any isolated `-I` replay mode drifts from `6e1349cb679ffda44162135bbeac536c5603339f061fdd93a95086631446268c`.
