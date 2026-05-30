"""Run Q1 and Q2 multiple times and report mean / std of the stage timings."""
import argparse
import csv
import os
import statistics
import sys
from typing import Callable

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from query1 import run as run_q1
from query2 import run as run_q2


def benchmark(name: str, fn: Callable, input_path: str, output_path: str,
              iterations: int, warmup: int) -> list:
    """Run `fn` (warmup + iterations) times. The warmup runs are discarded."""
    print(f"\n=== Benchmark: {name} | warmup={warmup} | measured={iterations} ===")
    runs = []
    total = iterations + warmup
    for i in range(total):
        is_warmup = i < warmup
        tag = "[warmup]" if is_warmup else f"[run {i - warmup + 1}/{iterations}]"
        print(f"\n{tag} Running {name}...")
        times = fn(input_path, output_path)
        if not is_warmup:
            times["end_to_end"] = sum(times.values())
            runs.append(times)
    return runs


def summarize(runs: list) -> dict:
    if not runs:
        return {}
    stages = runs[0].keys()
    summary = {}
    for stage in stages:
        values = [r[stage] for r in runs]
        summary[stage] = {
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
        }
    return summary


def print_summary(query_name: str, summary: dict) -> None:
    print(f"\n--- Summary {query_name} ---")
    print(f"{'Stage':<18}{'Mean (s)':>12}{'Std (s)':>12}{'Min (s)':>12}{'Max (s)':>12}")
    print("-" * 66)
    for stage, stats in summary.items():
        print(
            f"{stage:<18}"
            f"{stats['mean']:>12.3f}{stats['std']:>12.3f}"
            f"{stats['min']:>12.3f}{stats['max']:>12.3f}"
        )


def save_raw_runs(path: str, all_runs: dict) -> None:
    rows = []
    for query_name, runs in all_runs.items():
        for i, times in enumerate(runs, start=1):
            row = {"query": query_name, "iteration": i, **times}
            rows.append(row)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"\n[BENCHMARK] raw runs saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark Q1 and Q2")
    parser.add_argument("--input", default="data", help="CSV directory or glob")
    parser.add_argument("--iterations", type=int, default=5,
                        help="Measured iterations (excluding warmup)")
    parser.add_argument("--warmup", type=int, default=1,
                        help="Warmup iterations (discarded)")
    parser.add_argument("--output-prefix", default="results",
                        help="Prefix for output dirs. Use 'hdfs://namenode:9000/results' for HDFS.")
    parser.add_argument("--output-csv", default="benchmarks/runs.csv")
    args = parser.parse_args()

    bench_dir = os.path.dirname(args.output_csv)
    if bench_dir and not bench_dir.startswith("hdfs://"):
        os.makedirs(bench_dir, exist_ok=True)

    all_runs = {}
    summaries = {}

    for name, fn in [("Q1", run_q1), ("Q2", run_q2)]:
        out = f"{args.output_prefix.rstrip('/')}/{name.lower()}"
        runs = benchmark(name, fn, args.input, out, args.iterations, args.warmup)
        all_runs[name] = runs
        summaries[name] = summarize(runs)

    save_raw_runs(args.output_csv, all_runs)

    print("\n" + "=" * 66)
    print(" FINAL BENCHMARK SUMMARY")
    print("=" * 66)
    for name, summary in summaries.items():
        print_summary(name, summary)


if __name__ == "__main__":
    main()
