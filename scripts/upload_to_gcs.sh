#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUCKET="${GCS_BUCKET:?Set GCS_BUCKET, e.g. export GCS_BUCKET=my-bucket}"
PREFIX="${GCS_PREFIX:-data}"

USERS_CSV="$ROOT/data/users.csv"
ADDRESSES_CSV="$ROOT/data/addresses.csv"

if [[ ! -f "$USERS_CSV" || ! -f "$ADDRESSES_CSV" ]]; then
  echo "CSVs not found under $ROOT/data. Generate them first:" >&2
  echo "  python data_generator/generate_data.py" >&2
  exit 1
fi

DEST="gs://${BUCKET}/${PREFIX}/"
gsutil cp "$USERS_CSV" "$ADDRESSES_CSV" "$DEST"
echo "Uploaded users.csv and addresses.csv to ${DEST}"
