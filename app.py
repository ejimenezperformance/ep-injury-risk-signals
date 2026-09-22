"""
app.py
Early Injury-Risk Signal Dashboard
Emerson Performance (EP) | Streamlit

Run with: streamlit run app.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "src"))

import streamlit as st
import pandas as pd

from config import EP_NAVY, EP_OFFWHITE, INJURY_COHORT, CONTROL_COHORT, PRE_EVENT_WINDOW_DAYS
from data_loader import load_raw
from features import build_signal_table
from analysis import build_comparison_report
from visualization import plot_velocity_trajectories, plot_signal_boxplot

st.set_page_config(page_title="EP | Early Injury-Risk Signals", layout="wide")

st.markdown(
    f"""
    <style>
    .main {{ background-color: {EP_OFFWHITE}; }}
    h1, h2, h3 {{ color: {EP_NAVY}; font-family: 'Poppins', sans-serif; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("EP Baseball Intelligence")
st.sidebar.markdown(f"**Pre-event window:** {PRE_EVENT_WINDOW_DAYS} days")
st.sidebar.markdown(f"**Injury cases:** {len(INJURY_COHORT)}")
st.sidebar.markdown(f"**Control cases:** {len(CONTROL_COHORT)}")

page = st.sidebar.radio(
    "Navigation",
    [
        "1 — Executive Summary",
        "2 — Case Cohort",
        "3 — Velocity Trajectories",
        "4 — Statistical Comparison",
    ],
)

st.sidebar.warning(
    "⚠️ Exploratory / hypothesis-generating analysis only. "
    "Not a diagnostic or production model. See README for full guardrails."
)


@st.cache_data
def get_data():
    injury_df = load_raw("injury_cohort_raw.csv")
    control_df = load_raw("control_cohort_raw.csv")
    combined = pd.concat([injury_df, control_df], ignore_index=True)
    return combined


try:
    df = get_data()
    data_available = True
except FileNotFoundError:
    data_available = False

if not data_available:
    st.warning(
        "No local data found yet.\n\n"
        "Run first: `python src/data_loader.py` to download the injury and "
        "control cohorts from Baseball Savant."
    )
    st.stop()

signal_df = build_signal_table(df)

if page.startswith("1"):
    st.title("Early Injury-Risk Signal Pipeline — Executive Summary")
    st.markdown(
        """
        **Question:** In the weeks before a real, documented elbow/shoulder IL
        placement, do Statcast-derived signals (velocity decline, spin decline,
        release-point variability) look statistically different from an
        equivalent window in healthy comparison pitchers?

        This is an **exploratory, hypothesis-generating analysis** on a small,
        publicly-sourced cohort — not a diagnostic tool or production model.
        """
    )
    n_sufficient = signal_df["sufficient_data"].sum()
    st.metric("Cases with sufficient pre-event data", f"{n_sufficient} / {len(signal_df)}")
    st.dataframe(signal_df, use_container_width=True)

elif page.startswith("2"):
    st.title("Case Cohort")
    st.subheader("Injury cases (publicly sourced)")
    st.dataframe(pd.DataFrame(INJURY_COHORT), use_container_width=True)
    st.subheader("Control cases")
    st.dataframe(pd.DataFrame(CONTROL_COHORT), use_container_width=True)

elif page.startswith("3"):
    st.title("Velocity Trajectories Into Pre-Event Window")
    plot_velocity_trajectories(df)
    st.image(str(Path(__file__).resolve().parent / "outputs" / "figures" / "velocity_trajectories.png"))

elif page.startswith("4"):
    st.title("Statistical Comparison: Injury vs Control")
    comparison = build_comparison_report(signal_df)
    st.dataframe(
        comparison.style.format({"mean_injury": "{:.3f}", "mean_control": "{:.3f}", "p_value": "{:.3f}", "cohens_d": "{:.3f}"}),
        use_container_width=True,
    )
    st.caption(
        "Mann-Whitney U test (non-parametric, robust to small samples) + Cohen's d "
        "effect size. p < 0.05 with a small n should be read as suggestive, not "
        "confirmatory — replication with a larger cohort is the necessary next step."
    )

    metric_choice = st.selectbox(
        "Plot a signal",
        ["velocity_slope_mph_per_day", "spin_slope_rpm_per_day", "extension_slope_ft_per_day",
         "release_x_variability", "release_z_variability"],
    )
    plot_signal_boxplot(signal_df, metric_choice, "signal_boxplot.png")
    st.image(str(Path(__file__).resolve().parent / "outputs" / "figures" / "signal_boxplot.png"))
