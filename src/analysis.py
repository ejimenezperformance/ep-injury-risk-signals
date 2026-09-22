"""
analysis.py
Comparacion estadistica (no un modelo de ML) entre el grupo de lesion y
el grupo de control, sobre las senales calculadas en features.py.

Por que no un clasificador ML: el cohorte de lesion tiene n pequeno
(un puñado de casos publicos verificables). Forzar un XGBoost/regresion
logistica sobre esa muestra produciria un numero de AUC que aparenta
rigor pero no lo tiene. En su lugar, se reporta el n explicito, un test
no parametrico (Mann-Whitney U, robusto a muestras chicas y no-normales)
y el tamano de efecto (Cohen's d), dejando claro que esto es generador de
hipotesis, no un modelo predictivo listo para produccion.
"""

import numpy as np
import pandas as pd
from scipy import stats


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    if len(a) < 2 or len(b) < 2:
        return np.nan
    pooled_std = np.sqrt(((len(a) - 1) * a.std(ddof=1) ** 2 + (len(b) - 1) * b.std(ddof=1) ** 2) / (len(a) + len(b) - 2))
    if pooled_std == 0:
        return np.nan
    return (a.mean() - b.mean()) / pooled_std


def compare_groups(signal_df: pd.DataFrame, metric: str) -> dict:
    """Compara una metrica entre 'injury' y 'control' con Mann-Whitney U + Cohen's d."""
    injury_vals = signal_df.loc[signal_df["group"] == "injury", metric].dropna().values
    control_vals = signal_df.loc[signal_df["group"] == "control", metric].dropna().values

    result = {
        "metric": metric,
        "n_injury": len(injury_vals),
        "n_control": len(control_vals),
        "mean_injury": injury_vals.mean() if len(injury_vals) else np.nan,
        "mean_control": control_vals.mean() if len(control_vals) else np.nan,
        "p_value": np.nan,
        "cohens_d": np.nan,
    }

    if len(injury_vals) >= 2 and len(control_vals) >= 2:
        try:
            _, p = stats.mannwhitneyu(injury_vals, control_vals, alternative="two-sided")
            result["p_value"] = p
        except ValueError:
            pass
        result["cohens_d"] = cohens_d(injury_vals, control_vals)

    return result


def build_comparison_report(signal_df: pd.DataFrame) -> pd.DataFrame:
    """Corre compare_groups para todas las senales de interes y devuelve una tabla resumen."""
    metrics = [
        "velocity_slope_mph_per_day",
        "spin_slope_rpm_per_day",
        "extension_slope_ft_per_day",
        "release_x_variability",
        "release_z_variability",
    ]
    only_sufficient = signal_df[signal_df["sufficient_data"]]
    rows = [compare_groups(only_sufficient, m) for m in metrics]
    return pd.DataFrame(rows)
