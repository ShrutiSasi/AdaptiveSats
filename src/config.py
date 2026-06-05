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
TOTAL_BUDGET_USD = 1000.0

CALENDAR_CYCLES = [
    {"label": "Cycle 1: 2010-2013", "start": "2010-08-16", "end": "2013-12-31"},
    {"label": "Cycle 2: 2014-2017", "start": "2014-01-01", "end": "2017-12-31"},
    {"label": "Cycle 3: 2018-2021", "start": "2018-01-01", "end": "2021-12-31"},
    {"label": "Cycle 4: 2022-2023", "start": "2022-01-01", "end": "2023-12-31"},
]

HALVING_PERIODS = [
    {
        "label": "Before Nov 2012 Halving",
        "start": "2010-08-16", "end": "2012-11-27",
        "color": "rgba(173, 216, 230, 0.25)",
    },
    {
        "label": "2012-2016 Halving Cycle",
        "start": "2012-11-28", "end": "2016-07-08",
        "color": "rgba(144, 238, 144, 0.25)",
    },
    {
        "label": "2016-2020 Halving Cycle",
        "start": "2016-07-09", "end": "2020-05-10",
        "color": "rgba(176, 196, 222, 0.25)",
    },
    {
        "label": "2020-2024 Halving Cycle",
        "start": "2020-05-11", "end": "2023-12-31", # train set ends 2023-12-31
        "color": "rgba(238, 232, 170, 0.25)",
    },
]
