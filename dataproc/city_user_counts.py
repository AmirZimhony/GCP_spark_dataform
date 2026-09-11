#!/usr/bin/env python3
"""Count distinct users per city. Intended to run on Dataproc."""

from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Count distinct users per city")
    parser.add_argument(
        "--input",
        required=True,
        help="GCS or local path to addresses.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="GCS or local directory for city,user_count CSV",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spark = SparkSession.builder.appName("city_user_counts").getOrCreate()

    addresses = spark.read.option("header", True).csv(args.input)
    counts = (
        addresses.groupBy("city")
        .agg(F.countDistinct("user_id").alias("user_count"))
        .orderBy(F.col("user_count").desc(), F.col("city"))
    )
    counts.coalesce(1).write.mode("overwrite").option("header", True).csv(args.output)

    spark.stop()


if __name__ == "__main__":
    main()
