# Early Injury-Risk Signal Pipeline

A pipeline testing whether Statcast-derived signals (velocity decline, spin decline, release-point variability) are statistically distinguishable in the weeks before a real, publicly-documented elbow/shoulder IL placement, compared to an equivalent window in healthy pitchers. Built on the Emerson Performance (EP) EP-TSP framework.

—

Un pipeline que prueba si las señales derivadas de Statcast (declive de velocidad, declive de spin, variabilidad de release point) son estadísticamente distinguibles en las semanas previas a una colocación real y documentada públicamente en el IL por lesión de codo/hombro, comparadas contra una ventana equivalente en pitchers sanos. Construido sobre el framework EP-TSP de Emerson Performance (EP).

---

## ⚠️ Scope and Limits — Read First

**This is an exploratory, hypothesis-generating analysis on a small, publicly-sourced cohort. It is NOT a diagnostic tool, NOT a production/deployable model, and NOT a claim that any signal *causes* or *predicts* injury with clinical reliability.**

- Sample size is small and explicitly reported at every result (n per group).
- Injury dates come from public sources (MLB.com Transactions, press reports) with a documented confidence level per case (`exact` vs. `approx`).
- Bat/pitch-tracking proxies (velocity, spin, release point) describe *external performance behavior* as captured by Statcast — not internal joint kinematics, tissue status, or medical diagnosis.
- No causal claim is made. A declining signal before an IL placement is an *association in a small retrospective sample*, not evidence of mechanism.
- Any real-world application of a workflow like this would require: a much larger, systematically-built cohort; confounder control (workload, role, age, prior injury history); prospective validation; and direct involvement of a team's certified medical and performance staff.

—

**Este es un análisis exploratorio, generador de hipótesis, sobre un cohorte pequeño y de fuente pública. NO es una herramienta de diagnóstico, NO es un modelo de producción, y NO es una afirmación de que alguna señal *cause* o *prediga* lesión con confiabilidad clínica.** El tamaño de muestra se reporta explícitamente en cada resultado. Cualquier aplicación real requeriría un cohorte mucho más grande, control de variables de confusión, validación prospectiva, y la participación directa del personal médico certificado del equipo.

## Problem Statement

Teams invest heavily in injury prevention, but most public sabermetric work focuses on performance outcomes, not workload/risk signals. This project tests a specific, falsifiable question — do known pre-injury pitchers show a different velocity/spin/release-point pattern than healthy comparison pitchers in the weeks before their IL placement — using only public data, with the limitations stated up front rather than discovered later.

## Data Sources

- **Injury dates and types:** MLB.com Transactions, team injury reports, and press coverage (Sports Injury Central, FOX Sports, MLB.com), each case individually sourced and dated in `src/config.py::INJURY_COHORT`
- **Pitch-level Statcast data:** [pybaseball](https://github.com/jldbc/pybaseball) (`statcast_pitcher`), player IDs resolved automatically via `playerid_lookup`

## Methodology

1. For each injury case, pull the 42-day Statcast window immediately before the IL date
2. For each control case, pull an equivalent 42-day window around a **date-matched reference point** (paired to a specific injury case's timing, to avoid confounding by season-stage fatigue affecting both groups equally)
3. Compute per-case signals: velocity slope, spin-rate slope, extension slope (all via simple linear regression over the window), plus release-point (x/z) standard deviation
4. Flag cases with insufficient pre-event data (common for early-season injuries, where the window falls partly in spring training with sparse Statcast coverage) — these are excluded from the comparison, not silently included. A case needs ≥5 distinct pitching appearances and ≥100 pitches in the window to qualify (calibrated to what a starter — ~8 outings max in 42 days — or reliever can realistically produce; an earlier draft of this pipeline used a 21-day threshold that no real pitcher could ever satisfy)
5. Compare injury vs. control groups per signal using Mann-Whitney U (non-parametric, appropriate for small/non-normal samples) and Cohen's d effect size

## Why Not a Machine Learning Classifier

The injury cohort has a small n (a handful of publicly verifiable cases). Training an XGBoost or logistic regression classifier on that sample would produce an AUC or accuracy number that *looks* rigorous but isn't — it would overfit and the metric would be close to meaningless. Reporting an explicit n, a non-parametric statistical test, and an effect size is the honest version of this analysis at this sample size. Scaling to a real classifier is the natural next step once the cohort is 10x larger.

## Injury Cohort (starting seed — expand before drawing firm conclusions)

| Player | Team | IL Date | Injury Type | Date Confidence |
|---|---|---|---|---|
| Gavin Hollowell | CHC | 2026-07-31 | Shoulder inflammation | exact |
| Justin Steele | CHC | 2026-03-25 | Elbow flexor strain | exact |
| Cade Horton | CHC | 2026-04-05 | UCL damage (elbow) | exact |
| Andrew Kittredge | BAL | 2026-03-22 | Shoulder inflammation | exact |
| Nestor Cortes | MIL | 2025-04-04 | Elbow flexor strain | exact |
| Blake Snell | LAD | 2025-04-03 | Shoulder inflammation | exact |
| Cody Bradford | TEX | 2025-03-24 | Elbow sprain | exact |
| Pablo López | MIN | 2025-06-05 | Shoulder (teres major strain) | approx |
| Tyler Mahle | TEX | 2025-06-10 | Shoulder (rotator cuff strain) | approx |
| Nathan Eovaldi | TEX | 2026-08-09 | Right posterior elbow inflammation | exact |
| Garrett Whitlock | BOS | 2026-08-13 | Right elbow inflammation | exact |

Several early-season cases (Steele, Horton, Kittredge, Cortes, Snell, Bradford) have limited in-season pre-injury history and will likely be flagged `sufficient_data = False` — this is expected and handled by the pipeline, not a bug.

## Audit Log

| Check | Result |
|---|---|
| Injury cohort dates cross-checked against MLB.com Transactions text | PASS — 9/11 `exact`, 2/11 `approx` (Eovaldi and Whitlock upgraded to `exact` after verifying against MLB.com/Rangers PR/Boston Globe; only López and Mahle remain `approx`) |
| `sufficient_data` threshold realism check | **FIXED** — an earlier draft used `MIN_DAYS_ACTIVE_REQUIRED=21` in a 42-day window, which no pitcher (starter or reliever) can mathematically reach; recalibrated to 5 |
| Control cohort date-matching | **FIXED** — controls now paired to specific injury-case reference dates instead of all pointing at one calendar date |
| Leftover ML/SHAP references from an earlier design iteration | PASS — none found; `analysis.py` and README explicitly document the decision not to use a classifier |
| Statistical method appropriateness for small n | PASS — Mann-Whitney U + Cohen's d, no forced ML classifier |

## Limitations

- Small n, explicitly reported — not powered for strong statistical claims
- Control cohort is illustrative (n=2) and must be expanded with a proper randomized sample before real conclusions
- No confounder control yet (workload, role, age, prior injury history)
- Injury-type heterogeneity (flexor strain vs. UCL tear vs. inflammation) may have different signal signatures — pooling them is a simplification
- Retrospective only — no prospective validation yet
- `approx` confidence dates may be off by several days, adding noise to the pre-event window boundary

## Reproducibility

```bash
pip install -r requirements.txt
python src/data_loader.py        # resolves player IDs, downloads injury + control cohorts
jupyter notebook notebooks/01_injury_signal_analysis.ipynb
streamlit run app.py             # 4-page dashboard
```

---

Emerson Jimenez | Emerson Performance (EP)
