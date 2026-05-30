"""Spark session setup and CSV loader."""
import os

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType,
)

from utils import RELEVANT_COLS


# Declaring the schema by hand avoids the second pass that inferSchema does.
FLIGHT_SCHEMA = StructType([
    StructField("YEAR", IntegerType(), True),
    StructField("MONTH", IntegerType(), True),
    StructField("DAY_OF_MONTH", IntegerType(), True),
    StructField("OP_UNIQUE_CARRIER", StringType(), True),
    StructField("OP_CARRIER_FL_NUM", IntegerType(), True),
    StructField("ORIGIN_AIRPORT_ID", IntegerType(), True),
    StructField("ORIGIN_CITY_MARKET_ID", IntegerType(), True),
    StructField("ORIGIN_STATE_ABR", StringType(), True),
    StructField("DEST_AIRPORT_ID", IntegerType(), True),
    StructField("DEST_CITY_MARKET_ID", IntegerType(), True),
    StructField("DEST_STATE_ABR", StringType(), True),
    StructField("CRS_DEP_TIME", IntegerType(), True),
    StructField("DEP_TIME", DoubleType(), True),
    StructField("DEP_DELAY", DoubleType(), True),
    StructField("CRS_ARR_TIME", IntegerType(), True),
    StructField("ARR_TIME", DoubleType(), True),
    StructField("ARR_DELAY", DoubleType(), True),
    StructField("CANCELLED", DoubleType(), True),
    StructField("CANCELLATION_CODE", StringType(), True),
    StructField("DIVERTED", DoubleType(), True),
    StructField("ACTUAL_ELAPSED_TIME", DoubleType(), True),
    StructField("DISTANCE", DoubleType(), True),
    StructField("CARRIER_DELAY", DoubleType(), True),
    StructField("WEATHER_DELAY", DoubleType(), True),
    StructField("NAS_DELAY", DoubleType(), True),
    StructField("SECURITY_DELAY", DoubleType(), True),
    StructField("LATE_AIRCRAFT_DELAY", DoubleType(), True),
])


def build_spark(app_name: str) -> SparkSession:
    # SPARK_MASTER comes from the env when running via spark-submit on the
    # docker cluster; falls back to local[*] for direct python execution.
    master = os.environ.get("SPARK_MASTER", "local[*]")
    return (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def load_flights(spark: SparkSession, path: str) -> DataFrame:
    return (
        spark.read
        .option("header", "true")
        .schema(FLIGHT_SCHEMA)
        .csv(path)
        .select(*RELEVANT_COLS)
    )
