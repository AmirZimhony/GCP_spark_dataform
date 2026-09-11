# Data engineering home assignment

Generate 1M users/addresses, load them to GCS, model them in BigQuery with Dataform, and count users per city on Dataproc.

```
.
├── data_generator/
│   └── generate_data.py
├── dataform/
│   ├── workflow_settings.yaml
│   ├── package.json
│   └── definitions/
│       ├── raw_users.sqlx
│       ├── raw_addresses.sqlx
│       ├── users_incremental.sqlx
│       ├── addresses_incremental.sqlx
│       └── users_with_addresses.sqlx
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

Edit [`dataform/workflow_settings.yaml`](dataform/workflow_settings.yaml):

- `defaultProject`: GCP project
- `defaultLocation`: BigQuery location
- `vars.gcsBucket`: same bucket as the upload step

Pipeline:

1. `raw_users` / `raw_addresses` — BigQuery external tables over the GCS CSVs
2. `users_incremental` / `addresses_incremental` — MERGE on `user_id` / `address_id`, filtered by `updated_at` on incremental runs
3. `users_with_addresses` — users left-joined to addresses

```bash
cd dataform
npm install
npx @dataform/cli compile
npx @dataform/cli run
```

## 4. Dataproc — users per city

```bash
gcloud dataproc jobs submit pyspark dataproc/city_user_counts.py \
  --cluster=YOUR_CLUSTER \
  --region=europe-west1 \
  -- \
  --input=gs://$GCS_BUCKET/data/addresses.csv \
  --output=gs://$GCS_BUCKET/output/city_user_counts
```

Writes a single CSV with `city,user_count`, ordered by count descending. Tel Aviv should be 500,000.

Local check (if Spark is installed):

```bash
spark-submit dataproc/city_user_counts.py \
  --input=data/addresses.csv \
  --output=/tmp/city_user_counts
```
