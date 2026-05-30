# Docker Compose stack — HDFS + Spark

This directory contains the Phase 2 setup: a self-contained Big Data cluster
that satisfies the project's mandatory requirement of **reading the dataset
from HDFS and writing the results back to HDFS**.

## Services

| Service        | What it does                       | Web UI                  |
| -------------- | ---------------------------------- | ----------------------- |
| `namenode`     | HDFS master (metadata, file index) | http://localhost:9870   |
| `datanode`     | HDFS worker (actual file blocks)   | http://localhost:9864   |
| `spark-master` | Spark coordinator                  | http://localhost:8080   |
| `spark-worker` | Spark executor                     | http://localhost:8081   |

The project root is mounted into the Spark containers at `/app`, so
`spark-submit` can find `query1.py`, `query2.py`, etc.

## End-to-end workflow

Run all commands **from the project root** (`~/sabd_project1`).

### 1. Bring the cluster up

```bash
docker compose -f docker/docker-compose.yml up -d
```

Wait ~30s for HDFS to finish booting. Check status:

```bash
docker compose -f docker/docker-compose.yml ps
```

All four services should report `Up` / healthy.

### 2. Upload the CSVs to HDFS

```bash
bash docker/ingest_to_hdfs.sh
```

This copies `data/*.csv` into `hdfs:///flights/` and creates `hdfs:///results/`.

### 3. Run a query against HDFS

```bash
bash docker/run_on_hdfs.sh query1
bash docker/run_on_hdfs.sh query2
```

Each script invokes `spark-submit` inside the `sabd_spark_master` container,
pointing the query at `hdfs://namenode:9000/flights/*.csv` and writing its
output to `hdfs://namenode:9000/results/<queryN>`.

### 4. Pull the result CSVs back from HDFS

```bash
mkdir -p results_hdfs
docker exec sabd_namenode hdfs dfs -get /results/query1 /tmp/q1
docker cp sabd_namenode:/tmp/q1 results_hdfs/q1
docker exec sabd_namenode hdfs dfs -get /results/query2 /tmp/q2
docker cp sabd_namenode:/tmp/q2 results_hdfs/q2
```

### 5. Optional: run the benchmark suite on HDFS

```bash
bash docker/run_on_hdfs.sh benchmark
```

### 6. Shut the cluster down

```bash
docker compose -f docker/docker-compose.yml down            # keep data
docker compose -f docker/docker-compose.yml down --volumes  # also wipe HDFS
```

## Inspecting HDFS by hand

```bash
docker exec sabd_namenode hdfs dfs -ls /flights
docker exec sabd_namenode hdfs dfs -du -h /flights
docker exec sabd_namenode hdfs dfsadmin -report
```

Or just open http://localhost:9870 in a browser.
