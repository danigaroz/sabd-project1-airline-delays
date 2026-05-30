#!/usr/bin/env bash
# Pull query result CSVs from HDFS back into the local filesystem
# under results_hdfs/{q1,q2}/ so they can be plotted and shipped.
#
# Run from the project root:  bash docker/pull_results.sh
set -euo pipefail

NAMENODE="sabd_namenode"
LOCAL_DIR="results_hdfs"

mkdir -p "$LOCAL_DIR"

for q in query1 query2; do
    short=${q/query/q}                # query1 -> q1
    target="$LOCAL_DIR/$short"
    echo "[$q] downloading hdfs:///results/$q  ->  $target/"
    rm -rf "$target" /tmp/"$q"
    docker exec "$NAMENODE" hdfs dfs -get "/results/$q" /tmp/"$q"
    docker cp "$NAMENODE":/tmp/"$q" "$target"
    docker exec "$NAMENODE" rm -rf /tmp/"$q"
done

echo ""
echo "Local copies:"
find "$LOCAL_DIR" -type f | sort

echo ""
echo "Quick peek at the CSVs (skipping _SUCCESS markers):"
for csv in "$LOCAL_DIR"/q1/part-*.csv "$LOCAL_DIR"/q2/part-*.csv; do
    [ -f "$csv" ] || continue
    echo "--- $csv ---"
    cat "$csv"
done
