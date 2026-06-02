# Configuration file for the AdaptiveSats project

from pathlib import Path

def _find_root() -> Path:
    """ Walk up from src/ to the project root. """
    return Path(__file__).resolve().parent.parent

ROOT = _find_root()
DATA_DIR = ROOT / "data"
RAW_PATH = DATA_DIR / "raw" / "brk_metrics.parquet"
COL_DROP_FILE = DATA_DIR / "columns_to_drop.csv"
TRAIN_PATH = DATA_DIR / "processed" / "train.parquet"
TEST_PATH = DATA_DIR / "processed" / "test.parquet"
FIGURES_DIR = ROOT / "docs" / "figures"

# External data source used by stacksats strategy
STACKSATS_DATA_PATH = Path.home() / ".stacksats" / "data" / "bitcoin_analytics.parquet"

# Shared constants
SPLIT_YEAR = 2024

