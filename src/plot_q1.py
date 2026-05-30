"""Plots for Q1: monthly average departure delay and cancellation rate."""
import argparse
import glob
import os

import matplotlib.pyplot as plt
import pandas as pd


MONTH_NAMES = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr"}
AIRLINE_COLORS = {"AA": "#C8102E", "DL": "#003366"}


def load_q1_csv(results_dir: str) -> pd.DataFrame:
    files = glob.glob(os.path.join(results_dir, "part-*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV file found in {results_dir}")
    df = pd.read_csv(files[0])
    df["month_label"] = df["month"].map(MONTH_NAMES)
    return df.sort_values(["month", "airline"])


def plot_avg_delay(df: pd.DataFrame, output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    for airline in ["AA", "DL"]:
        sub = df[df["airline"] == airline]
        ax.plot(
            sub["month_label"], sub["dep_delay_mean"],
            marker="o", linewidth=2, markersize=8,
            label=airline, color=AIRLINE_COLORS[airline],
        )
    ax.set_xlabel("Month (2025)")
    ax.set_ylabel("Average departure delay (minutes)")
    ax.set_title("Q1 - Monthly average departure delay: AA vs DL")
    ax.legend(title="Airline")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
    print(f"[PLOT] saved {output_path}")


def plot_cancellation_rate(df: pd.DataFrame, output_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    months = df["month_label"].unique()
    x = range(len(months))
    width = 0.35
    for i, airline in enumerate(["AA", "DL"]):
        sub = df[df["airline"] == airline].sort_values("month")
        offset = (i - 0.5) * width
        ax.bar(
            [v + offset for v in x], sub["cancellation_rate"],
            width=width, label=airline, color=AIRLINE_COLORS[airline],
        )
    ax.set_xticks(list(x))
    ax.set_xticklabels(months)
    ax.set_xlabel("Month (2025)")
    ax.set_ylabel("Cancellation rate (%)")
    ax.set_title("Q1 - Monthly cancellation rate: AA vs DL")
    ax.legend(title="Airline")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
    print(f"[PLOT] saved {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Plot Q1 results")
    parser.add_argument("--input", default="results/q1", help="Directory with Q1 CSV")
    parser.add_argument("--output", default="plots", help="Directory to save plots")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    df = load_q1_csv(args.input)
    print("Q1 results:")
    print(df.to_string(index=False))

    plot_avg_delay(df, os.path.join(args.output, "q1_avg_dep_delay.png"))
    plot_cancellation_rate(df, os.path.join(args.output, "q1_cancellation_rate.png"))


if __name__ == "__main__":
    main()
