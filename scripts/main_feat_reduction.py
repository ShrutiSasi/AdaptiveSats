import polars as pl
import pandas as pd
import numpy as np
from scipy.cluster import hierarchy
from scipy.spatial.distance import squareform
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import gc
import logging
from pathlib import Path

# importing family classification logic
from metric_classifier import MetricClassifier 

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ClusteringConfig:
    
    SCRIPT_DIR = Path(__file__).resolve().parent
    ROOT_DIR = SCRIPT_DIR.parent
    
    # Path logic: root/data/brk_metrics.parquet
    PARQUET_PATH = ROOT_DIR / "data" / "brk_metrics.parquet"
    OUTPUT_DIR = ROOT_DIR / "output"
    DATE_COL = "day_utc"
    METRIC_COL = "metric"
    VALUE_COL = "value"
    
    # Distance thresholds (0.0 = identical, 1.0 = no correlation)
    LOCAL_THRESHOLD = 0.5   
    GLOBAL_THRESHOLD = 0.6  
    
    @staticmethod
    def extract_family(metric_name: str) -> str:
        """
        Uses the MetricClassifier class imported from metric_classifier.py
        to assign a domain-specific category.
        """
        return MetricClassifier.assign_category(metric_name)

def make_stationary(df_wide: pd.DataFrame) -> pd.DataFrame:
    """Transforms raw time-series into percentage changes to ensure stationarity."""
    df_stationary = df_wide.ffill(limit=7).pct_change(fill_method=None)
    df_stationary = df_stationary.replace([np.inf, -np.inf], np.nan).dropna(how='all')
    return df_stationary.fillna(0)

def find_central_metrics(df_features: pd.DataFrame, threshold: float) -> list:
    """Finds representative metrics for each cluster based on correlation."""
    if df_features.empty: return []
    if df_features.shape[1] == 1: return df_features.columns.tolist()

    # Standardize and correlate
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df_features)
    corr_matrix = pd.DataFrame(scaled_data, columns=df_features.columns).corr().abs().fillna(0)

    # Convert to distance matrix
    dist_matrix = np.clip(1 - corr_matrix.values, 0, 1)
    np.fill_diagonal(dist_matrix, 0)
    condensed_dist = squareform(dist_matrix)

    # Hierarchical Clustering
    Z = hierarchy.linkage(condensed_dist, method='complete')
    cluster_labels = hierarchy.fcluster(Z, t=threshold, criterion='distance')

    # Select the metric with the highest average correlation in its cluster
    cluster_dict = defaultdict(list)
    for i, label in enumerate(cluster_labels):
        cluster_dict[label].append(df_features.columns[i])

    survivors = []
    for metrics in cluster_dict.values():
        if len(metrics) == 1:
            survivors.append(metrics[0])
        else:
            sub_corr = corr_matrix.loc[metrics, metrics]
            survivors.append(sub_corr.mean(axis=1).idxmax())
    return survivors

def main():
    logging.info(f"Scanning parquet: {ClusteringConfig.PARQUET_PATH}")
    lf = pl.scan_parquet(ClusteringConfig.PARQUET_PATH)
    
    unique_metrics = lf.select(ClusteringConfig.METRIC_COL).unique().collect().to_series().to_list()
    
    # PHASE 1: Grouping Custom Families
    family_map = defaultdict(list)
    for m in unique_metrics:
        family = ClusteringConfig.extract_family(m)
        family_map[family].append(m)
    
    logging.info(f"Identified {len(family_map)} families from {len(unique_metrics)} metrics.")
    
    local_survivors = []

    # Local Pruning within each Family
    for family, metrics in family_map.items():
        if family == "Other" or len(metrics) == 1:
            local_survivors.extend(metrics)
            continue
            
        logging.info(f"Pruning Family: {family} ({len(metrics)} metrics)")
        
        df_family = (
            lf.filter(pl.col(ClusteringConfig.METRIC_COL).is_in(metrics))
            .collect().to_pandas()
            .pivot(index=ClusteringConfig.DATE_COL, columns=ClusteringConfig.METRIC_COL, values=ClusteringConfig.VALUE_COL)
        )
        
        df_stat = make_stationary(df_family)
        survivors = find_central_metrics(df_stat, ClusteringConfig.LOCAL_THRESHOLD)
        local_survivors.extend(survivors)
        
        del df_family, df_stat
        gc.collect()

    # PHASE 2: Global Pruning
    logging.info(f"Global Pruning: {len(local_survivors)} candidates...")
    df_global = (
        lf.filter(pl.col(ClusteringConfig.METRIC_COL).is_in(local_survivors))
        .collect().to_pandas()
        .pivot(index=ClusteringConfig.DATE_COL, columns=ClusteringConfig.METRIC_COL, values=ClusteringConfig.VALUE_COL)
    )
    
    df_global_stat = make_stationary(df_global)
    final_features = find_central_metrics(df_global_stat, ClusteringConfig.GLOBAL_THRESHOLD)
    
    output_file = ClusteringConfig.OUTPUT_DIR / "final_accumulation_features.csv"
    pd.Series(final_features).to_csv(output_file, index=False)    
    logging.info(f"Results saved to: {output_file}")

if __name__ == "__main__":
    main()