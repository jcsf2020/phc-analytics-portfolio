from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = BASE_DIR / "out"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
SERVING_DIR = DATA_DIR / "serving"

# Watermark / incremental load
WATERMARK_FIELD = "updated_at"
STATE_FILE = DATA_DIR / "_pipeline_state.json"

# Ensure directories exist
for d in [BRONZE_DIR, SILVER_DIR, GOLD_DIR, SERVING_DIR]:
    d.mkdir(parents=True, exist_ok=True)
