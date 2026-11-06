from pyspark.sql import SparkSession, functions as F

BUCKET = "feast-spark-lab"
OUTPUT_PATH = f"s3a://{BUCKET}/offline/driver_daily_stats"

spark = (
    SparkSession.builder.appName("daily-driver-features")
    .master("local[2]")
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")
    .config(
        "spark.jars.packages",
        "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262",
    )
    .config("spark.hadoop.fs.s3a.endpoint", "http://127.0.0.1:9000")
    .config("spark.hadoop.fs.s3a.endpoint.region", "ap-southeast-1")
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# Raw trip events for the last 5 days, spread across 5 drivers
raw_trips = (
    spark.range(0, 500)
    .withColumn("driver_id", (F.col("id") % 5 + 1001).cast("long"))
    .withColumn("day_offset", F.floor(F.rand(7) * 5).cast("int"))
    .withColumn("trip_day", F.expr("date_sub(current_date(), day_offset)"))
    .withColumn("distance_km", F.round(F.rand(11) * 20 + 1, 2))
    .withColumn("rating", F.round(F.rand(13) * 2 + 3, 2))
)

# Daily features per driver, with UTC timestamps for Feast
daily_features = (
    raw_trips.groupBy("driver_id", "trip_day")
    .agg(
        F.count("*").cast("long").alias("daily_trips"),
        F.round(F.avg("rating"), 2).alias("avg_rating"),
        F.round(F.sum("distance_km"), 2).alias("total_distance_km"),
    )
    .withColumn("event_timestamp", F.to_timestamp(F.date_format("trip_day", "yyyy-MM-dd 00:00:00")))
    .withColumn("created", F.current_timestamp())
    .drop("trip_day")
)

daily_features.coalesce(1).write.mode("overwrite").parquet(OUTPUT_PATH)

print("Rows written:", daily_features.count())
daily_features.orderBy("driver_id", "event_timestamp").show(10, truncate=False)

spark.stop()
