from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("city-user-count").getOrCreate()

spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.shuffle.partitions", "20")

df = (
    spark.read
    .format("bigquery")
    .option(
        "table",
        "project-d2e743fd-f7fe-4894-a24.home_Assignments.users_with_addresses"
    )
    .load()
)

# Force ALL rows to shuffle according to city.
skewed = df.repartition(20, "city")

# Then perform the required summary.
result = skewed.groupBy("city").count()

print("AQE:", spark.conf.get("spark.sql.adaptive.enabled"))
result.explain("formatted")

result.show(100, truncate=False)