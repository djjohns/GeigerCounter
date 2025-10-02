#!/bin/sh
set -e

# Force local connection during init; ignore PGHOST/DATABASE_URL from .env
unset PGHOST DATABASE_URL

# Optionally also ignore PGPASSWORD; local socket auth is configured to allow init
unset PGPASSWORD

DB="${POSTGRES_DB}"
USER="${POSTGRES_USER}"
TABLE="${GMC_TABLE}"
CSV_DIR="${CSV_DIR}"

echo "Seeding CSVs from: $CSV_DIR into table: $TABLE on DB: $DB"

found_any=false
for f in "$CSV_DIR"/*.csv; do
  [ -e "$f" ] || continue
  found_any=true
  echo "Loading: $f"
  # Use the Unix-domain socket directory used by the entrypoint
  psql --no-psqlrc -v ON_ERROR_STOP=1 \
       -h /var/run/postgresql \
       -U "$USER" -d "$DB" \
       -c "\COPY $TABLE (datetime, count, unit, mode, reference_datetime, notes)
           FROM '$f' WITH (FORMAT csv, HEADER true)"
done

if [ "$found_any" = false ]; then
  echo "No CSV files found in $CSV_DIR — skipping seed."
fi

echo "CSV load complete."
