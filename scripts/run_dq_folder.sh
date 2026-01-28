#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/run_dq_folder.sh sql/analytics/data_quality/dim_customer
#
# Requires:
#   DATABASE_URL set in env.

FOLDER="${1:-}"
if [[ -z "$FOLDER" ]]; then
  echo "ERROR: missing folder argument"
  echo "Usage: $0 <folder>"
  exit 2
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL is not set"
  echo "Example:"
  echo '  export DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"'
  exit 2
fi

if [[ ! -d "$FOLDER" ]]; then
  echo "ERROR: folder not found: $FOLDER"
  exit 2
fi

mapfile -t FILES < <(find "$FOLDER" -maxdepth 1 -type f -name "*.sql" | sort)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "ERROR: no .sql files found in: $FOLDER"
  exit 2
fi

echo "Running data quality checks in: $FOLDER"
for f in "${FILES[@]}"; do
  echo "==> $f"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
done

echo "OK: all checks executed"
