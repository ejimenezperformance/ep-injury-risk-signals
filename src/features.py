"""
features.py
Calcula, por cada caso (jugador + evento), la pendiente de declive de
velocidad y spin rate a lo largo de la ventana pre-evento, y la
variabilidad del punto de release — las "senales" que se comparan entre
el grupo de lesion y el grupo de control.

Guardrail: una pendiente negativa de velocidad describe un patron
observado en los datos de Statcast, no una causa fisiologica. Es un
descriptor de rendimiento externo que genera hipotesis, no un diagnostico.
"""

import numpy as np
import pandas as pd
from config import MIN_PITCHES_REQUIRED, MIN_DAYS_ACTIVE_REQUIRED


def _linear_slope(x_days: np.ndarray, y: np.ndarray) -> float:
    """Pendiente de una regresion lineal simple y ~ x_days (unidad/dia)."""
    if len(x_days) < 3 or np.all(x_days == x_days[0]):
        return np.nan
    slope, _ = np.polyfit(x_days, y, 1)
    return slope


def compute_case_signals(df_case: pd.DataFrame) -> dict:
    """
    Calcula las senales de un solo caso (un jugador, una ventana pre-evento).
    df_case debe venir ya filtrado a un solo player_name/case_event_date.
    """
    df_case = df_case.dropna(subset=["game_date"]).sort_values("game_date").copy()
    n_pitches = len(df_case)
    n_days_active = df_case["game_date"].nunique()

    result = {
        "n_pitches": n_pitches,
        "n_days_active": n_days_active,
        "sufficient_data": (n_pitches >= MIN_PITCHES_REQUIRED) and (n_days_active >= MIN_DAYS_ACTIVE_REQUIRED),
        "velocity_slope_mph_per_day": np.nan,
        "spin_slope_rpm_per_day": np.nan,
        "release_x_variability": np.nan,
        "release_z_variability": np.nan,
        "extension_slope_ft_per_day": np.nan,
    }

    if n_pitches == 0:
        return result

    x_days = (df_case["game_date"] - df_case["game_date"].min()).dt.days.values.astype(float)

    if "release_speed" in df_case.columns:
        result["velocity_slope_mph_per_day"] = _linear_slope(x_days, df_case["release_speed"].values)
    if "release_spin_rate" in df_case.columns:
        result["spin_slope_rpm_per_day"] = _linear_slope(x_days, df_case["release_spin_rate"].values)
    if "release_extension" in df_case.columns:
        result["extension_slope_ft_per_day"] = _linear_slope(x_days, df_case["release_extension"].values)
    if "release_pos_x" in df_case.columns:
        result["release_x_variability"] = df_case["release_pos_x"].std()
    if "release_pos_z" in df_case.columns:
        result["release_z_variability"] = df_case["release_pos_z"].std()

    return result


def build_signal_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica compute_case_signals a cada caso individual (agrupado por
    case_player_name + case_event_date + group) y arma la tabla comparativa
    completa, lista para el analisis estadistico.
    """
    if df.empty:
        return pd.DataFrame()

    rows = []
    group_cols = ["case_player_name", "case_event_date", "group"]
    extra_cols = ["case_injury_type", "case_date_confidence"]

    for keys, df_case in df.groupby(group_cols):
        signals = compute_case_signals(df_case)
        row = dict(zip(group_cols, keys))
        for col in extra_cols:
            if col in df_case.columns:
                row[col] = df_case[col].iloc[0]
        row.update(signals)
        rows.append(row)

    return pd.DataFrame(rows)
