"""
data_loader.py
Resuelve nombre -> MLBAM ID via pybaseball.playerid_lookup, y descarga la
ventana Statcast pre-evento (o pre-referencia, para controles) de cada
pitcher en el cohorte.
"""

import time
import pandas as pd
from pathlib import Path
from pybaseball import playerid_lookup, statcast_pitcher

from config import (
    DATA_RAW,
    PRE_EVENT_WINDOW_DAYS,
    INJURY_COHORT,
    CONTROL_COHORT,
)


def resolve_mlbam_id(last: str, first: str) -> int:
    """Busca el MLBAM ID de un jugador por nombre."""
    lookup = playerid_lookup(last, first)
    if lookup.empty:
        raise ValueError(f"No se encontro MLBAM ID para {first} {last}")
    # Prioriza el registro con temporada de debut mas reciente si hay varios
    lookup = lookup.sort_values("mlb_played_last", ascending=False)
    return int(lookup.iloc[0]["key_mlbam"])


def fetch_pre_event_window(mlbam_id: int, event_date: str, window_days: int = PRE_EVENT_WINDOW_DAYS) -> pd.DataFrame:
    """Descarga Statcast del pitcher en los N dias previos a event_date."""
    end_dt = pd.Timestamp(event_date) - pd.Timedelta(days=1)
    start_dt = end_dt - pd.Timedelta(days=window_days)
    df = statcast_pitcher(start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"), mlbam_id)
    return df


def build_injury_cohort_dataset(cohort: list = None, delay_sec: float = 1.0) -> pd.DataFrame:
    """
    Descarga la ventana pre-evento para cada caso del cohorte de lesion y
    concatena todo en un solo DataFrame, con columnas adicionales de
    identificacion del caso (player_name, il_date, injury_type, group='injury').
    """
    cohort = cohort or INJURY_COHORT
    frames = []
    for case in cohort:
        name = f"{case['first']} {case['last']}"
        try:
            mlbam_id = resolve_mlbam_id(case["last"], case["first"])
            df = fetch_pre_event_window(mlbam_id, case["il_date"])
            if df.empty:
                print(f"AVISO: sin datos para {name} antes de {case['il_date']}")
                continue
            df["case_player_name"] = name
            df["case_event_date"] = case["il_date"]
            df["case_injury_type"] = case["injury_type"]
            df["case_date_confidence"] = case["date_confidence"]
            df["group"] = "injury"
            frames.append(df)
            print(f"OK: {name} — {len(df)} pitches en ventana pre-evento")
        except Exception as e:
            print(f"ERROR con {name}: {e}")
        time.sleep(delay_sec)  # cortesia con la API de Baseball Savant

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def build_control_cohort_dataset(cohort: list = None, window_days: int = PRE_EVENT_WINDOW_DAYS, delay_sec: float = 1.0) -> pd.DataFrame:
    """Igual que build_injury_cohort_dataset pero para el cohorte de control (pitchers sanos)."""
    cohort = cohort or CONTROL_COHORT
    frames = []
    for case in cohort:
        name = f"{case['first']} {case['last']}"
        try:
            mlbam_id = resolve_mlbam_id(case["last"], case["first"])
            df = fetch_pre_event_window(mlbam_id, case["reference_date"], window_days)
            if df.empty:
                print(f"AVISO: sin datos para {name}")
                continue
            df["case_player_name"] = name
            df["case_event_date"] = case["reference_date"]
            df["case_injury_type"] = "none (control)"
            df["case_date_confidence"] = "n/a"
            df["group"] = "control"
            frames.append(df)
            print(f"OK: {name} — {len(df)} pitches (control)")
        except Exception as e:
            print(f"ERROR con {name}: {e}")
        time.sleep(delay_sec)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def save_raw(df: pd.DataFrame, filename: str) -> Path:
    out_path = DATA_RAW / filename
    df.to_csv(out_path, index=False)
    print(f"Guardado: {out_path}")
    return out_path


def load_raw(filename: str) -> pd.DataFrame:
    path = DATA_RAW / filename
    if not path.exists():
        raise FileNotFoundError(f"No se encontro {path}. Corre python src/data_loader.py primero.")
    return pd.read_csv(path, parse_dates=["game_date"])


if __name__ == "__main__":
    print("=== Descargando cohorte de lesion ===")
    injury_df = build_injury_cohort_dataset()
    save_raw(injury_df, "injury_cohort_raw.csv")

    print("\n=== Descargando cohorte de control ===")
    control_df = build_control_cohort_dataset()
    save_raw(control_df, "control_cohort_raw.csv")
