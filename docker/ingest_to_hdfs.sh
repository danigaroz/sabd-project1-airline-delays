#!/usr/bin/env bash
# Copy local CSVs into HDFS under /flights.
# Run from the project root:  bash docker/ingest_to_hdfs.sh
set -euo pipefail

NAMENODE_CONTAINER="sabd_namenode"
HDFS_TARGET="/flights"
DATA_DIR="$(pwd)/data"

if [ ! -d "$DATA_DIR" ]; then
    echo "ERROR: $DATA_DIR not found. Run this script from the project root."
    exit 1
fi

echo "[1/4] Waiting for HDFS to be ready..."
for i in $(seq 1 30); do
    if docker exec "$NAMENODE_CONTAINER" hdfs dfs -ls / >/dev/null 2>&1; then
        echo "      HDFS is up."
        break
    fi
    echo "      retry $i/30..."
    sleep 2
done

echo "[2/4] (Re)creating HDFS directories..."
docker exec "$NAMENODE_CONTAINER" hdfs dfs -rm -r -f "$HDFS_TARGET" >/dev/null 2>&1 || true
docker exec "$NAMENODE_CONTAINER" hdfs dfs -mkdir -p "$HDFS_TARGET"
docker exec "$NAMENODE_CONTAINER" hdfs dfs -mkdir -p /results

echo "[3/4] Uploading CSVs..."
for csv in "$DATA_DIR"/*.csv; do
    fname=$(basename "$csv")
    echo "      -> $fname"
    docker cp "$csv" "$NAMENODE_CONTAINER":/tmp/"$fname"
    docker exec "$NAMENODE_CONTAINER" hdfs dfs -put -f /tmp/"$fname" "$HDFS_TARGET"/
    docker exec "$NAMENODE_CONTAINER" rm -f /tmp/"$fname"
done

echo "[4/4] Verification:"
docker exec "$NAMENODE_CONTAINER" hdfs dfs -ls "$HDFS_TARGET"

echo ""
echo "Done. Files are available under hdfs://namenode:9000$HDFS_TARGET/"
