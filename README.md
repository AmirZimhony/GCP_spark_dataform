# Users and addresses data pipeline

This repository is confidential. Do not copy, share, or republish it.

Generate 1M users/addresses, load them to GCS, model them in BigQuery with Dataform, and count users per city on Dataproc.

```
.
├── data_generator/
│   └── generate_data.py
├── workflow_settings.yaml
├── package.json
├── definitions/
│   ├── raw_users.sqlx
│   ├── raw_addresses.sqlx
│   ├── users_incremental.sqlx
│   ├── addresses_incremental.sqlx
│   └── users_with_addresses.sqlx
├── dataproc/
│   └── city_user_counts.py
├── scripts/
│   └── upload_to_gcs.sh
└── data/                  # generated CSVs (gitignored)
```

## 1. Generate CSVs

```bash
python3 -m venv .venv
source .venv/bin/activate
python data_generator/generate_data.py
```

Writes `data/users.csv` and `data/addresses.csv` (1,000,000 rows each, seed `42`):

- 500,000 addresses in Tel Aviv
- 500,000 addresses across 80 other Israeli cities (population-weighted)

Smoke test: `python data_generator/generate_data.py --n-users 1000`

## 2. Upload to GCS

Set a bucket, then:

```bash
export GCS_BUCKET=YOUR_GCS_BUCKET
chmod +x scripts/upload_to_gcs.sh
./scripts/upload_to_gcs.sh
```

Files land at `gs://$GCS_BUCKET/data/users.csv` and `gs://$GCS_BUCKET/data/addresses.csv`. Override the prefix with `GCS_PREFIX`.

## 3. Dataform (BigQuery)

Edit [`workflow_settings.yaml`](workflow_settings.yaml):

- `defaultProject`: GCP project
- `defaultLocation`: BigQuery location
- `vars.gcsBucket`: same bucket as the upload step

Pipeline:

1. `raw_users` / `raw_addresses` — BigQuery external tables over the GCS CSVs
2. `users_incremental` / `addresses_incremental` — MERGE on `user_id` / `address_id`, filtered by `updated_at` on incremental runs
3. `users_with_addresses` — users left-joined to addresses

```bash
npm install
npx @dataform/cli compile
npx @dataform/cli run
```

## 4. Dataproc — users per city

`dataproc/city_user_counts.py` reads `home_Assignments.users_with_addresses` from BigQuery (not the GCS CSVs). It disables AQE, repartitions by `city` into 20 partitions, then `groupBy("city").count()`. The job prints a formatted Spark plan and the city counts (Tel Aviv should be 500,000).

Submit as a serverless batch. `--deps-bucket` only stages the `.py` file for Dataproc; the table data still comes from BigQuery.

```bash
gcloud dataproc batches submit pyspark dataproc/city_user_counts.py \
  --region=europe-west1 \
  --version=2.3 \
  --deps-bucket=gs://home_assignments
```
