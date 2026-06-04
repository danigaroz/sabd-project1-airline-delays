# SABD 2025/26 — Project 1: Airline Delays Analysis with Spark and HDFS

**Author:** Daniel Garoz · M.Sc. Computer Engineering (Erasmus Exchange)
**Institution:** Università degli Studi di Roma "Tor Vergata"
**Course:** Sistemi e Architetture per Big Data — A.A. 2025/26
**Professors:** Valeria Cardellini, Matteo Nardelli

---

## Overview

End-to-end Big Data pipeline that analyses US Bureau of Transportation
Statistics on-time flight performance data using **Apache Spark** for
distributed processing and **HDFS** for distributed storage, both
deployed via **Docker Compose**.

The pipeline answers two analytical queries:

- **Query 1** — For airlines AA (American Airlines) and DL (Delta),
  compute monthly average / minimum / maximum departure delay and the
  cancellation rate.
- **Query 2** — Rank the top 10 airlines by average arrival delay
  (considering only carriers with ≥ 500 completed flights) and break
  down the contribution of the five delay causes for each one.

Each query is evaluated in two configurations: a local PySpark setup
on the host and a fully containerized HDFS+Spark cluster. Benchmark
results, plots and the final report are included in this repository.

## Dataset

The pipeline targets US BTS flight data for January–March 2025
(≈ 1.55 million records across three monthly CSVs, ~178 MB total).
The course specification refers to January–April 2025; the archive
available at the time of this work covered only the first three
months. This is documented as a constraint in the report.

## Repository structure

```
.
├── data/                          # input CSVs (gitignored)
├── docker/                        # Docker Compose stack for Phase 2
│   ├── docker-compose.yml         # HDFS + Spark cluster
│   ├── hadoop.env                 # Hadoop env variables for bde2020 images
│   ├── ingest_to_hdfs.sh          # upload local CSVs into HDFS
│   ├── run_on_hdfs.sh             # submit a query/benchmark to the cluster
│   ├── pull_results.sh            # download result CSVs from HDFS
│   └── README.md                  # Docker setup details
├── src/                           # PySpark source code
│   ├── utils.py                   # timing helpers, relevant column list
│   ├── preprocessing.py           # SparkSession config + schema-aware loader
│   ├── query1.py                  # Q1 implementation
│   ├── query2.py                  # Q2 implementation
│   ├── plot_q1.py                 # Q1 visualizations
│   ├── plot_q2.py                 # Q2 visualizations
│   └── benchmark.py               # benchmark harness (multi-iteration)
├── Results/                       # CSV deliverables (per project spec)
│   ├── q1/part-*.csv
│   └── q2/part-*.csv
├── plots/                         # PNG figures used by the report
│   ├── q1_avg_dep_delay.png
│   ├── q1_cancellation_rate.png
│   ├── q2_top10_ranking.png
│   └── q2_delay_causes.png
├── Report/                        # ACM/IEEE proceedings PDF + LaTeX source
│   └── main.tex
├── slides/                        # presentation Beamer source + script
│   ├── main.tex
│   └── SCRIPT.md                  # speaker script for the oral defense
├── benchmarks/                    # raw benchmark CSVs (per-iteration)
│   ├── runs.csv                   # local execution
│   └── runs_hdfs.csv              # HDFS cluster execution
└── README.md                      # this file
```

## Prerequisites

| Tool           | Version  | Used for                                       |
| -------------- | -------- | ---------------------------------------------- |
| Python         | 3.10+    | PySpark virtual environment                    |
| Java JRE       | 17       | Spark runtime                                  |
| Docker         | 20.10+   | Phase 2: containerized HDFS + Spark cluster    |
| Docker Compose | 2.x      | Multi-container orchestration                  |

The pipeline was developed and benchmarked on Ubuntu 24.04 under WSL2
(Windows 11).

## Quick start

### 1. Clone the repository

```bash
git clone <repository-url> sabd_project1
cd sabd_project1
```

### 2. Set up the Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyspark pandas matplotlib pyarrow
```

### 3. Download the dataset

The pre-processed dataset is provided through the course materials
(Teams, channel "Progetto 1"). Place the extracted CSVs in `data/`:

```
data/
├── 202501_T_ONTIME_REPORTING.csv
├── 202502_T_ONTIME_REPORTING.csv
└── 202503_T_ONTIME_REPORTING.csv
```

### 4. Run locally (Phase 1 — fast development)

```bash
python3 src/query1.py --input data --output results/q1
python3 src/query2.py --input data --output results/q2
python3 src/plot_q1.py --input results/q1 --output plots
python3 src/plot_q2.py --input results/q2 --output plots
```

### 5. Benchmark locally

```bash
python3 src/benchmark.py --input data --iterations 5 --warmup 1
```

### 6. Run on the containerized HDFS+Spark cluster (Phase 2)

```bash
# Start the cluster
docker compose -f docker/docker-compose.yml up -d

# Wait ~20 seconds for HDFS to finish initializing, then ingest the CSVs
bash docker/ingest_to_hdfs.sh

# Run the queries against HDFS
bash docker/run_on_hdfs.sh query1
bash docker/run_on_hdfs.sh query2

# Optional: run the benchmark suite against HDFS
bash docker/run_on_hdfs.sh benchmark

# Download the result CSVs from HDFS
bash docker/pull_results.sh

# Shut the cluster down (keeps data in HDFS volumes)
docker compose -f docker/docker-compose.yml down
```

Web UIs while the cluster is running:

| Service        | URL                          |
| -------------- | ---------------------------- |
| HDFS NameNode  | http://localhost:9870        |
| HDFS DataNode  | http://localhost:9864        |
| Spark Master   | http://localhost:8080        |
| Spark Worker   | http://localhost:8081        |

## Key design decisions

| Decision                 | Reason                                                 |
| ------------------------ | ------------------------------------------------------ |
| Explicit Spark schema    | Avoids the double pass that `inferSchema` requires    |
| `cache()` only in Q1     | Q1 reuses the filtered DataFrame; Q2 uses it once     |
| `shuffle.partitions = 8` | Matches host CPU count; the default 200 is wasteful   |
| `coalesce(1)` at output  | Produces a single CSV file as required by the spec    |
| NULL delay causes → 0    | BTS convention: causes are filled only when delay ≥ 15 |
| bde2020 Docker images    | Pre-configured for the HDFS + Spark wiring            |

## Experimental results (summary)

End-to-end execution time (mean ± standard deviation, 5 measured
iterations after 1 warm-up):

| Query | Local (venv)        | HDFS (cluster)        | Overhead |
| ----- | ------------------- | --------------------- | -------- |
| Q1    | 7.40 ± 1.17 s       | 22.12 ± 1.72 s        | 3.0×     |
| Q2    | 6.49 ± 2.36 s       | 19.15 ± 1.54 s        | 2.95×     |

See `Report/main.tex` for the full per-stage breakdown and the
discussion.

## Deliverables checklist

- [x] Spark implementations of Q1 and Q2 (DataFrame API, no Spark SQL)
- [x] Output CSV files in `Results/`
- [x] Plots in `plots/`
- [x] Dockerized HDFS + Spark cluster
- [x] Benchmark suite with mean/std across iterations
- [x] Report in IEEE proceedings format in `Report/`
- [x] Presentation slides in `slides/`

## License

Academic project, MIT-style use permitted for educational purposes.
