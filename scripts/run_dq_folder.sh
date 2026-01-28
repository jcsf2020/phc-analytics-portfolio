#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/run_dq_folder.sh sql/analytics/data_quality/dim_customer
#
# Contract:
#   - Every check query MUST return 0 rows to be valid.
#   - If any check returns >= 1 row, this script exits 1 (quality gate fail).
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

failed=0

for f in "${FILES[@]}"; do
  echo "==> $f"

  # psql flags:
  # -q : quiet (less noise)
  # -A : unaligned output (machine-friendly)
  # -t : tuples only (no headers)
  # -v ON_ERROR_STOP=1 : stop on SQL error (non-zero exit)
  out="$(psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -qAt -f "$f" || true)"

  if [[ -n "$out" ]]; then
    echo "FAIL: check returned rows in $f"
    echo "$out"
    failed=1
  else
    echo "PASS: 0 rows"
  fi
done

if [[ "$failed" -ne 0 ]]; then
  echo "DQ GATE: FAILED"
  exit 1
fi

echo "DQ GATE: PASSED"
exit 0
