import subprocess
import pandas as pd
import polars as pl
from pathlib import Path


def load_metric_wide(
    train_path: Path,
    filter_expr,
    nan_thresh: float = 0.5,
) -> pd.DataFrame:
    """Scan parquet, filter by expression, pivot wide, and clean.

    Parameters
    ----------
    filter_expr : polars Expr
        e.g. pl.col("metric").str.starts_with("cost_basis_")
             or pl.col("metric").is_in(SIGNAL_METRICS)

    Returns
    -------
    pd.DataFrame  indexed by day_utc, one column per metric, cleaned.
    """
    wide = (
        pl.scan_parquet(train_path)
        .filter(filter_expr)
        .collect()
        .pivot(values="value", index="day_utc", on="metric")
        .sort("day_utc")
        .to_pandas()
        .set_index("day_utc")
        .apply(pd.to_numeric, errors="coerce")
    )
    wide = wide.dropna(axis=1, thresh=int(nan_thresh * len(wide)))
    wide = wide.fillna(wide.median())
    wide = wide.loc[:, wide.nunique() > 1]
    return wide


def load_metrics(train_path: Path, metric_list: list[str]) -> pd.DataFrame:
    """Load a specific list of metrics and pivot wide."""
    return load_metric_wide(
        train_path,
        filter_expr=pl.col("metric").is_in(metric_list),
    )

def check_stacksats_data(path: Path, raw_path: Path) -> bool:
    """Check if the Stacksats data file exists and is readable."""
    try:
        if not raw_path.exists():
                raise FileNotFoundError(
                    f"Raw BRK metrics file not found at: {raw_path}. "
                    "Please update raw_brk_path to the correct location of brk_metrics.parquet."
                )
        
        if not path.exists():
            print(f"Prepared dataset not found at: {path}")
            print("Preparing StackSats analytics dataset...")            

            subprocess.run(
                [
                    "stacksats",
                    "data",
                    "prepare",
                    "--source",
                    str(raw_path),
                ],
                check=True,
            )

        if not path.exists():
            print(f"Preparation completed but dataset still not found at: {path}")
            return False
        else:
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"Error loading Stacksats data from {path}: {e}")
        return False