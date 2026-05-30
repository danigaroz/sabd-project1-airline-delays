"""Query 2: top 10 carriers by mean ARR_DELAY, with delay-cause breakdown.

NULLs in the five delay-cause columns are treated as 0. The BTS only
populates those columns when ARR_DELAY >= 15 min; coercing the NULLs
matches the interpretation "this cause did not contribute to the delay".
Dropping rows with NULLs would silently bias the average towards
delayed flights only.
"""
import argparse
import os
import sys

from pyspark.sql import functions as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preprocessing import build_spark, load_flights
from utils import timer


MIN_FLIGHTS = 500
TOP_N = 10
DELAY_CAUSES = [
    "CARRIER_DELAY", "WEATHER_DELAY", "NAS_DELAY",
    "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY",
]


def run(input_path: str, output_path: str) -> dict:
    times: dict = {}
    spark = build_spark("Q2_top10_arrdelay")
    spark.sparkContext.setLogLevel("WARN")

    with timer("loading", times):
        df = load_flights(spark, input_path)
        df.count()

    with timer("preprocessing", times):
        completed = df.filter(
            (F.col("CANCELLED") == 0) & (F.col("DIVERTED") == 0)
        )
        for cause in DELAY_CAUSES:
            completed = completed.withColumn(
                cause, F.coalesce(F.col(cause), F.lit(0.0))
            )

    with timer("computation", times):
        agg_exprs = [
            F.count("*").alias("num_flights"),
            F.round(F.mean("ARR_DELAY"), 2).alias("arrdelay_mean"),
        ]
        for cause in DELAY_CAUSES:
            agg_exprs.append(
                F.round(F.mean(cause), 2).alias(f"{cause.lower()}_mean")
            )

        per_carrier = (
            completed.groupBy("OP_UNIQUE_CARRIER")
            .agg(*agg_exprs)
            .filter(F.col("num_flights") >= MIN_FLIGHTS)
            .orderBy(F.col("arrdelay_mean").desc())
            .limit(TOP_N)
        )

        result = per_carrier.select(
            F.col("OP_UNIQUE_CARRIER").alias("carrier"),
            "num_flights", "arrdelay_mean",
            "carrier_delay_mean", "weather_delay_mean", "nas_delay_mean",
            "security_delay_mean", "late_aircraft_delay_mean",
        )

    with timer("output", times):
        result.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)

    result.show(20, truncate=False)
    spark.stop()
    return times


def main():
    parser = argparse.ArgumentParser(description="Run Query 2")
    parser.add_argument("--input", default="data", help="CSV directory or glob")
    parser.add_argument("--output", default="results/q2", help="Output CSV directory")
    args = parser.parse_args()

    times = run(args.input, args.output)
    total = sum(times.values())
    print(f"\n[Q2] Stage breakdown: {times}")
    print(f"[Q2] End-to-end time: {total:.3f}s")


if __name__ == "__main__":
    main()
