"""
visualization.py
Graficas del pipeline de senales de riesgo, estilo EP.
"""

import matplotlib.pyplot as plt
import seaborn as sns

from config import EP_NAVY, EP_GOLD, EP_PALETTE, OUTPUTS_FIGURES


def _apply_ep_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams["axes.edgecolor"] = EP_NAVY
    plt.rcParams["text.color"] = EP_NAVY
    plt.rcParams["axes.labelcolor"] = EP_NAVY
    plt.rcParams["xtick.color"] = EP_NAVY
    plt.rcParams["ytick.color"] = EP_NAVY


def plot_velocity_trajectories(df, save_as: str = "velocity_trajectories.png"):
    """Una linea por caso: velocidad promedio por dia dentro de su ventana pre-evento."""
    _apply_ep_style()
    plt.figure(figsize=(12, 7))

    for (name, group_label), df_case in df.groupby(["case_player_name", "group"]):
        daily = df_case.dropna(subset=["release_speed"]).groupby("game_date")["release_speed"].mean()
        if daily.empty:
            continue
        days_from_start = (daily.index - daily.index.min()).days
        color = EP_NAVY if group_label == "injury" else EP_GOLD
        alpha = 0.85 if group_label == "injury" else 0.5
        plt.plot(days_from_start, daily.values, color=color, alpha=alpha, linewidth=1.5, label=f"{name} ({group_label})")

    plt.title("Velocity Trajectory Into Pre-Event Window — Injury (navy) vs Control (gold)", fontsize=13, color=EP_NAVY)
    plt.xlabel("Days into pre-event window")
    plt.ylabel("Release Speed (mph)")
    plt.legend(fontsize=7, loc="lower left", ncol=2)
    plt.tight_layout()
    plt.savefig(OUTPUTS_FIGURES / save_as, dpi=150)
    plt.close()


def plot_signal_boxplot(signal_df, metric: str, save_as: str = None):
    """Boxplot comparando una senal entre grupo de lesion y control."""
    if metric not in signal_df.columns:
        print(f"{metric} no disponible.")
        return
    _apply_ep_style()
    only_sufficient = signal_df[signal_df["sufficient_data"]]
    plt.figure(figsize=(6, 5))
    sns.boxplot(data=only_sufficient, x="group", y=metric, hue="group", palette=[EP_NAVY, EP_GOLD], legend=False)
    sns.stripplot(data=only_sufficient, x="group", y=metric, color="black", size=6, alpha=0.6)
    plt.title(f"{metric}: Injury vs Control", fontsize=13, color=EP_NAVY)
    plt.tight_layout()
    if save_as:
        plt.savefig(OUTPUTS_FIGURES / save_as, dpi=150)
    plt.close()
