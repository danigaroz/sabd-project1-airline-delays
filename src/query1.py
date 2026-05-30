"""Query 1: monthly DEP_DELAY stats and cancellation rate for AA and DL."""
import argparse
import os
import sys

from pyspark.sql import functions as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import build_spark, load_flights
from utils import timer


TARGET_AIRLINES = ["AA", "DL"]


def run(input_path: str, output_path: str) -> dict:
    times: dict = {}
    spark = build_spark("Q1_AA_DL_monthly")
    spark.sparkContext.setLogLevel("WARN")

    with timer("loading", times):
        df = load_flights(spark, input_path).filter(
            F.col("OP_UNIQUE_CARRIER").isin(TARGET_AIRLINES)
        )
        # Same df feeds both the delay-stats branch and the cancellation-rate
        # branch, so we cache it. The count() forces materialization here
        # rather than during the first heavy action below.
        df = df.cache()
        df.count()

    with timer("preprocessing", times):
        non_cancelled = df.filter(F.col("CANCELLED") == 0)

    with timer("computation", times):
        delay_stats = (
            non_cancelled.groupBy("MONTH", "OP_UNIQUE_CARRIER")
            .agg(
                F.round(F.mean("DEP_DELAY"), 2).alias("dep_delay_mean"),
                F.min("DEP_DELAY").alias("dep_delay_min"),
                F.max("DEP_DELAY").alias("dep_delay_max"),
            )
        )

        cancellation_rate = (
            df.groupBy("MONTH", "OP_UNIQUE_CARRIER")
            .agg(
                F.round(F.sum("CANCELLED") / F.count("*") * 100, 4)
                .alias("cancellation_rate")
            )
        )

        result = (
            delay_stats.join(cancellation_rate, ["MONTH", "OP_UNIQUE_CARRIER"])
            .select(
                F.col("MONTH").alias("month"),
                F.col("OP_UNIQUE_CARRIER").alias("airline"),
                "dep_delay_mean", "dep_delay_min", "dep_delay_max",
                "cancellation_rate",
            )
            .orderBy("month", "airline")
        )

    with timer("output", times):
        # coalesce(1) so the spec-required single CSV is produced.
        result.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)

    result.show(20, truncate=False)
    spark.stop()
    return times


def main():
    parser = argparse.ArgumentParser(description="Run Query 1")
    parser.add_argument("--input", default="data", help="CSV directory or glob")
    parser.add_argument("--output", default="results/q1", help="Output CSV directory")
    args = parser.parse_args()

    times = run(args.input, args.output)
    total = sum(times.values())
    print(f"\n[Q1] Stage breakdown: {times}")
    print(f"[Q1] End-to-end time: {total:.3f}s")


if __name__ == "__main__":
    main()
