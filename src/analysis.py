"""Metric categorization and statistical utilities for AdaptiveSats."""

import numpy as np
import pandas as pd
import polars as pl
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import linkage
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant


def assign_category(metric: str) -> str:
    """Assign a category to a metric based on its name."""
    m = str(metric).lower()

    profitability_sopr_exact = {
        "adjusted_sopr_30d_ema",
        "adjusted_sopr_7d_ema",
        "sopr_30d_ema",
        "sopr_7d_ema",
        "net_realized_pnl_7d_ema",
        "realized_profit_7d_ema",
        "realized_loss_7d_ema",
    }

    market_valuation_exact = {
        "investor_price_ratio_1m_sma",
        "investor_price_ratio_1w_sma",
        "investor_price_ratio_1y_sma",
        "investor_price_ratio_2y_sma",
        "investor_price_ratio_4y_sma",
        "investor_price_ratio_sma",
        "pi_cycle",
        "puell_multiple",
        "reserve_risk",
        "sell_side_risk_ratio_30d_ema",
        "sell_side_risk_ratio_7d_ema",
    }

    network_activity_exact = {
        "sent_14d_ema",
        "sent_14d_ema_btc",
        "sent_14d_ema_usd",
        "sent_in_loss_14d_ema",
        "sent_in_loss_14d_ema_btc",
        "sent_in_loss_14d_ema_usd",
        "sent_in_profit_14d_ema",
        "sent_in_profit_14d_ema_btc",
        "sent_in_profit_14d_ema_usd",
        "vocdd",
        "vocdd_365d_median",
        "vocdd_cumulative",
        "hash_rate_1m_sma",
        "hash_rate_1w_sma",
        "hash_rate_1y_sma",
        "hash_rate_2m_sma",
    }

    block_reward_exact = {
        "subsidy_usd_1y_sma",
    }

    technical_indicators_exact = {
        "macd_histogram",
        "macd_line",
        "macd_signal",
        "rsi_14d",
        "rsi_14d_max",
        "rsi_14d_min",
        "rsi_average_gain_14d",
        "rsi_average_loss_14d",
        "rsi_gains",
        "rsi_losses",
        "stoch_d",
        "stoch_k",
        "stoch_rsi",
        "stoch_rsi_d",
        "stoch_rsi_k",
        "sortino_1m",
        "sortino_1w",
        "sortino_1y",
        "downside_returns",
        "downside_1m_sd_sd",
        "downside_1m_sd_sma",
        "downside_1w_sd_sd",
        "downside_1w_sd_sma",
        "downside_1y_sd_sd",
        "downside_1y_sd_sma",
    }

    if m in profitability_sopr_exact:
        return "Profitability & SOPR"

    if m in market_valuation_exact:
        return "Market & Valuation"

    if m in network_activity_exact:
        return "Network Activity"

    if m in block_reward_exact:
        return "Block Reward Distributions"

    if m in technical_indicators_exact:
        return "Technical Indicators"

    if m in (
        "day_utc", "dateindex", "monthindex", "weekindex",
        "timestamp", "datetime"
    ):
        return "Metadata"

    if m.startswith("constant_"):
        return "Metadata"

    if m.startswith(("year_", "epoch_", "halvingepoch")):
        return "Age & Halving Cohorts"

    if m in ("days_before_next_halving", "blocks_before_next_halving"):
        return "Age & Halving Cohorts"

    if "pool" in m:
        return "Pool-Specific Economics"

    if "dominance" in m:
        return "Entities"

    if m.startswith("coinbase_usd_"):
        return "Market & Valuation"

    if m.startswith("coinbase_btc_"):
        return "Block Reward Distributions"

    if m.startswith("coinbase_"):
        return "Block Reward Distributions"

    if m.startswith("unclaimed_rewards"):
        return "Block Reward Distributions"

    if m.startswith("price_"):
        return "Price"

    if m.startswith(("utxo_", "utxos_")):
        return "UTXO Age Cohorts"

    if m in ("utxo_count", "exact_utxo_count"):
        return "UTXO Age Cohorts"

    if m.startswith(("sth_", "lth_")):
        return "Holder Cohorts"

    if m.startswith("addrs_"):
        return "Address Distribution by Balance"

    if m in ("total_addr_count",):
        return "Address Distribution by Balance"

    if m.startswith(("empty_outputs_", "emptyoutput_", "unknown_outputs_")):
        return "Network Activity"

    if m.startswith((
        "p2a_", "p2ms_", "p2pk_", "p2pkh_",
        "p2pk33_", "p2pk65_", "p2sh_",
        "p2wpkh_", "p2wsh_", "p2tr_",
        "p2sh_p2wpkh_", "p2sh_p2wsh_"
    )):
        return "Address Activity by Tech Type"

    if m.startswith((
        "dca_", "lump_sum_", "1d_", "1w_", "1m_", "3m_",
        "6m_", "1y_", "2y_", "3y_", "4y_", "5y_",
        "6y_", "8y_", "10y_", "_30d_", "30d_",
        "60d_", "90d_", "180d_", "365d_", "24h_"
    )):
        return "Benchmarks & DCA"

    if any(m.startswith(p) for p in (
        "rsi_", "macd_", "stoch_", "sortino_", "downside_"
    )):
        return "Technical Indicators"

    if any(k in m for k in (
        "_rsi", "_macd", "_stoch"
    )):
        return "Technical Indicators"

    if any(m.startswith(p) for p in (
        "sopr", "adjusted_sopr", "net_realized", "unrealized_",
        "pain_", "profit_", "capitulation_", "sell_side",
        "invested_capital", "neg_realized", "neg_unrealized",
        "nupl", "peak_regret", "loss_", "net_unrealized"
    )):
        return "Profitability & SOPR"

    if any(k in m for k in (
        "profit", "loss", "pnl", "sopr",
        "realized_profit", "realized_loss",
        "unrealized_profit", "unrealized_loss",
        "net_realized", "net_unrealized",
        "capitulation", "peak_regret"
    )):
        return "Profitability & SOPR"

    if any(m.startswith(p) for p in (
        "supply_", "subsidy_", "inflation_", "circulating_",
        "illiquid_", "liquid_", "highly_liquid_", "hodl_",
        "liveliness", "vaultedness", "cdd_", "coindays_",
        "coinblocks_", "cointime_", "thermocap_", "thermo_"
    )):
        return "Supply & Scarcity"

    if any(k in m for k in (
        "supply", "scarcity", "hodl", "liveliness",
        "vaultedness", "cointime", "coindays",
        "coinblocks", "coin_days", "cdd",
        "thermocap", "thermo_cap"
    )):
        return "Supply & Scarcity"

    if any(m.startswith(p) for p in (
        "block_", "blocks_", "tx_", "transaction_",
        "transactions_", "address_", "addr_", "fee_",
        "fees_", "hash_", "hashrate_", "hash_rate_",
        "sent_", "received_", "difficulty", "segwit_",
        "taproot_", "height_", "mempool_", "vsize_",
        "weight_", "input_", "inputs_", "output_",
        "outputs_", "empty_addr_", "new_addr_", "opreturn_"
    )):
        return "Network Activity"

    if any(k in m for k in (
        "block", "tx_", "transaction", "mempool",
        "hashrate", "hash_rate", "difficulty",
        "segwit", "taproot", "vsize", "weight",
        "input_count", "output_count", "outputs_per_sec",
        "inputs_per_sec", "opreturn", "empty_addr",
        "new_addr", "addr_count", "sent"
    )):
        return "Network Activity"

    if m in (
        "adjusted_value_created", "adjusted_value_destroyed",
        "value_created", "value_destroyed", "sent", "first_height"
    ):
        return "Network Activity"

    entity_metric_patterns = (
        "_blocks_mined", "_blocks_mined_cumulative",
        "_blocks_since_block", "_coinbase",
        "_days_since_block", "_fee", "_fee_btc",
        "_fee_usd", "_fee_cumulative",
        "_fee_btc_cumulative", "_fee_usd_cumulative",
        "_subsidy"
    )

    if any(p in m for p in entity_metric_patterns):
        return "Entities"

    entity_keywords = (
        "bitcoincom_", "btccom_", "foundry_", "foundryusa_",
        "slush_", "ghash_", "ghashio_", "btcguild_",
        "asicminer_", "antpool_", "f2pool_", "viabtc_",
        "binancepool_", "braiins_", "luxor_", "mara_",
        "riot_", "bitfury_", "bitfarms_", "nicehash_",
        "eclipsemc_", "eligius_", "btcc_", "btctop_",
        "cloudhashing_", "bitclub_", "bitminter_",
        "ozcoin_", "ocean_", "axbt_", "bcmonster_"
    )

    if m.startswith(entity_keywords):
        return "Entities"

    if any(m.startswith(p) for p in (
        "market_cap", "realized_cap", "mvrv", "nvt",
        "investor_", "cost_basis", "active_", "vaulted_",
        "true_market", "lower_price", "upper_price",
        "greed_", "oracle_", "terminal_", "balanced_",
        "delta_", "average_cap", "thermo_price",
        "max_cost_basis", "min_cost_basis",
        "btc_velocity", "gini"
    )):
        return "Market & Valuation"

    if any(k in m for k in (
        "price", "market_cap", "realized_cap", "mvrv", "nvt",
        "valuation", "cost_basis", "true_market",
        "terminal_price", "balanced_price", "delta_price",
        "average_cap", "velocity", "gini",
        "annualized_volume", "growth_rate", "cap_growth_rate",
        "net_sentiment", "greed_index", "pain_index",
        "realized_value", "spot_invested_capital_percentile"
    )):
        return "Market & Valuation"

    mining_keywords = (
        "miner_", "miners_", "mining_",
        "block_reward", "block_rewards",
        "hashrate_", "hash_rate", "subsidy_", "reward_"
    )

    if any(k in m for k in mining_keywords):
        return "Block Reward Distributions"

    return "Other"


def compute_correlation_linkage(
    wide_df: pd.DataFrame,
    corr_method: str = "pearson",
    linkage_method: str = "ward",
) -> tuple[pd.DataFrame, np.ndarray]:
    """Compute correlation matrix and Ward linkage.

    Returns
    -------
    corr : pd.DataFrame
    Z    : np.ndarray  (linkage matrix for dendrogram / fcluster)
    """
    corr = wide_df.corr(method=corr_method)
    dist = squareform(1 - corr.abs(), checks=False)
    Z = linkage(dist, method=linkage_method)
    return corr, Z


def compute_vif_clusters(
    train_pl: pl.DataFrame,
    cluster_dict: dict[int, list[str]],
    vif_threshold: float = 10.0,
) -> dict[int, list[str]]:
    """Run VIF analysis over each cluster.

    Parameters
    ----------
    train_pl     : polars DataFrame in long format (metric, value, day_utc).
    cluster_dict : {cluster_id: [metric_names]}.
    vif_threshold: flag columns with VIF above this value.

    Returns
    -------
    dict[int, list[str]]  — cluster id → high-VIF column names.
    """
    high_vif: dict[int, list[str]] = {}

    for i, metrics in cluster_dict.items():
        print(f"\nCluster {i}:")
        x = (
            train_pl.filter(pl.col("metric").is_in(metrics))
            .pivot(index="day_utc", on="metric", values="value")
            .drop("day_utc")
            .to_pandas()
            .dropna()
        )
        if x.shape[1] < 2:
            print("  Skipping — need at least 2 features for VIF")
            continue

        X = add_constant(x)
        vif = pd.Series(
            [variance_inflation_factor(X.values, j) for j in range(X.shape[1])],
            index=X.columns,
        )
        vif = vif.drop("const", errors="ignore")
        high_vif[i] = vif[vif > vif_threshold].index.tolist()
        print(vif.sort_values(ascending=False).to_string())
        print(f"\n  High VIF cols (>{vif_threshold}): {high_vif[i]}")

    return high_vif
