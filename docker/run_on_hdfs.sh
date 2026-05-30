#!/usr/bin/env bash
# Submit a query to the dockerized Spark cluster, reading from and writing
# results to HDFS.
#
# Usage:    bash docker/run_on_hdfs.sh <query1|query2|benchmark>
# Examples: bash docker/run_on_hdfs.sh query1
#           bash docker/run_on_hdfs.sh benchmark
set -euo pipefail

QUERY="${1:-}"
if [ -z "$QUERY" ]; then
    echo "Usage: $0 <query1|query2|benchmark>"
    exit 1
fi

SCRIPT="/app/src/${QUERY}.py"
INPUT="hdfs://namenode:9000/flights/*.csv"
OUTPUT="hdfs://namenode:9000/results/${QUERY}"

echo "Submitting $SCRIPT to spark://spark-master:7077"
echo "  input : $INPUT"
echo "  output: $OUTPUT"
echo ""

if [ "$QUERY" = "benchmark" ]; then
    # benchmark.py: --input HDFS, outputs also into HDFS
    docker exec -e SPARK_MASTER="spark://spark-master:7077" sabd_spark_master \
        /spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --deploy-mode client \
        "$SCRIPT" \
        --input "$INPUT" \
        --output-prefix "hdfs://namenode:9000/results" \
        --output-csv "/app/benchmarks/runs_hdfs.csv" \
        --iterations 5 --warmup 1
else
    docker exec -e SPARK_MASTER="spark://spark-master:7077" sabd_spark_master \
        /spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --deploy-mode client \
        "$SCRIPT" \
        --input "$INPUT" \
        --output "$OUTPUT"
fi

echo ""
echo "Result available in HDFS:"
docker exec sabd_namenode hdfs dfs -ls "/results/${QUERY}" || true
