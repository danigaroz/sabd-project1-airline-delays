"""Plots for Q2: top 10 carriers ranking and delay-cause breakdown."""
import argparse
import glob
import os

import matplotlib.pyplot as plt
import pandas as pd


CAUSE_COLS = [
    "carrier_delay_mean", "weather_delay_mean", "nas_delay_mean",
    "security_delay_mean", "late_aircraft_delay_mean",
]
CAUSE_LABELS = ["Carrier", "Weather", "NAS", "Security", "Late Aircraft"]
CAUSE_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]


def load_q2_csv(results_dir: str) -> pd.DataFrame:
    files = glob.glob(os.path.join(results_dir, "part-*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV file found in {results_dir}")
    df = pd.read_csv(files[0])
    return df.sort_values("arrdelay_mean", ascending=False).reset_index(drop=True)


def plot_ranking(df: pd.DataFrame, output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(df["carrier"], df["arrdelay_mean"], color="#3a76b8")
    ax.set_xlabel("Airline (carrier code)")
    ax.set_ylabel("Average arrival delay (minutes)")
    ax.set_title("Q2 - Top 10 airlines by average arrival delay")
    ax.grid(True, axis="y", alpha=0.3)
    for i, v in enumerate(df["arrdelay_mean"]):
        ax.text(i, v + 0.2, f"{v:.1f}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
    print(f"[PLOT] saved {output_path}")


def plot_causes(df: pd.DataFrame, output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = [0.0] * len(df)
    for cause, label, color in zip(CAUSE_COLS, CAUSE_LABELS, CAUSE_COLORS):
        values = df[cause].tolist()
        ax.bar(df["carrier"], values, bottom=bottom, label=label, color=color)
        bottom = [b + v for b, v in zip(bottom, values)]
    ax.set_xlabel("Airline (carrier code)")
    ax.set_ylabel("Average delay contribution (minutes)")
    ax.set_title("Q2 - Avg delay contribution by cause (top 10 airlines)")
    ax.legend(title="Delay cause", loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
    print(f"[PLOT] saved {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Plot Q2 results")
    parser.add_argument("--input", default="results/q2", help="Directory with Q2 CSV")
    parser.add_argument("--output", default="plots", help="Directory to save plots")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    df = load_q2_csv(args.input)
    print("Q2 results:")
    print(df.to_string(index=False))

    plot_ranking(df, os.path.join(args.output, "q2_top10_ranking.png"))
    plot_causes(df, os.path.join(args.output, "q2_delay_causes.png"))


if __name__ == "__main__":
    main()
