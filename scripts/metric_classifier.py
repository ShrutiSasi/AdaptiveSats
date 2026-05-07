import re
import ast

class MetricClassifier:
    @staticmethod
    def assign_category(metric: str) -> str:
        m = str(metric).lower()

        # 1. Exact Match Overrides
        profitability_sopr_exact = {
            "adjusted_sopr_30d_ema", "adjusted_sopr_7d_ema", "sopr_30d_ema",
            "sopr_7d_ema", "net_realized_pnl_7d_ema", "realized_profit_7d_ema",
            "realized_loss_7d_ema",
        }
        market_valuation_exact = {
            "investor_price_ratio_1m_sma", "investor_price_ratio_1w_sma",
            "investor_price_ratio_1y_sma", "investor_price_ratio_2y_sma",
            "investor_price_ratio_4y_sma", "investor_price_ratio_sma",
            "pi_cycle", "puell_multiple", "reserve_risk",
            "sell_side_risk_ratio_30d_ema", "sell_side_risk_ratio_7d_ema",
        }
        network_activity_exact = {
            "sent_14d_ema", "sent_14d_ema_btc", "sent_14d_ema_usd",
            "sent_in_loss_14d_ema", "sent_in_loss_14d_ema_btc", "sent_in_loss_14d_ema_usd",
            "sent_in_profit_14d_ema", "sent_in_profit_14d_ema_btc", "sent_in_profit_14d_ema_usd",
            "vocdd", "vocdd_365d_median", "vocdd_cumulative",
            "hash_rate_1m_sma", "hash_rate_1w_sma", "hash_rate_1y_sma", "hash_rate_2m_sma",
        }
        block_reward_exact = {"subsidy_usd_1y_sma"}
        technical_indicators_exact = {
            "macd_histogram", "macd_line", "macd_signal", "rsi_14d", "rsi_14d_max",
            "rsi_14d_min", "rsi_average_gain_14d", "rsi_average_loss_14d",
            "rsi_gains", "rsi_losses", "stoch_d", "stoch_k", "stoch_rsi",
            "stoch_rsi_d", "stoch_rsi_k", "sortino_1m", "sortino_1w", "sortino_1y",
            "downside_returns", "downside_1m_sd_sd", "downside_1m_sd_sma",
            "downside_1w_sd_sd", "downside_1w_sd_sma", "downside_1y_sd_sd", "downside_1y_sd_sma",
        }

        if m in profitability_sopr_exact: return "Profitability & SOPR"
        if m in market_valuation_exact: return "Market & Valuation"
        if m in network_activity_exact: return "Network Activity"
        if m in block_reward_exact: return "Block Reward Distributions"
        if m in technical_indicators_exact: return "Technical Indicators"

        # 2. Metadata & Time
        if m in ("day_utc", "dateindex", "monthindex", "weekindex", "timestamp", "datetime"):
            return "Metadata"
        if m.startswith("constant_"): return "Metadata"
        if m.startswith(("year_", "epoch_", "halvingepoch")): return "Age & Halving Cohorts"
        if m in ("days_before_next_halving", "blocks_before_next_halving"): return "Age & Halving Cohorts"

        # 3. Keyword / Prefix Groups
        if "pool" in m: return "Pool-Specific Economics"
        if "dominance" in m: return "Entities"
        if m.startswith("coinbase_usd_"): return "Market & Valuation"
        if m.startswith(("coinbase_btc_", "coinbase_", "unclaimed_rewards")): return "Block Reward Distributions"
        if m.startswith("price_"): return "Price"
        if m.startswith(("utxo_", "utxos_")) or m in ("utxo_count", "exact_utxo_count"): return "UTXO Age Cohorts"
        if m.startswith(("sth_", "lth_")): return "Holder Cohorts"
        if m.startswith("addrs_") or m == "total_addr_count": return "Address Distribution by Balance"
        
        # 4. Tech Types (p2sh, p2wpkh, etc)
        tech_prefixes = ("p2a_", "p2ms_", "p2pk_", "p2pkh_", "p2pk33_", "p2pk65_", "p2sh_", 
                         "p2wpkh_", "p2wsh_", "p2tr_", "p2sh_p2wpkh_", "p2sh_p2wsh_")
        if m.startswith(tech_prefixes): return "Address Activity by Tech Type"
        if m.startswith(("empty_outputs_", "emptyoutput_", "unknown_outputs_")): return "Network Activity"

        # 5. Benchmarks & DCA
        dca_prefixes = ("dca_", "lump_sum_", "1d_", "1w_", "1m_", "3m_", "6m_", "1y_", "2y_", 
                        "3y_", "4y_", "5y_", "6y_", "8y_", "10y_", "_30d_", "30d_", "60d_", 
                        "90d_", "180d_", "365d_", "24h_")
        if m.startswith(dca_prefixes): return "Benchmarks & DCA"

        # 6. Technical Indicators (Keywords)
        if any(m.startswith(p) for p in ("rsi_", "macd_", "stoch_", "sortino_", "downside_")): return "Technical Indicators"
        if any(k in m for k in ("_rsi", "_macd", "_stoch")): return "Technical Indicators"

        # 7. Profitability (Keywords)
        prof_prefixes = ("sopr", "adjusted_sopr", "net_realized", "unrealized_", "pain_", "profit_", 
                         "capitulation_", "sell_side", "invested_capital", "neg_realized", 
                         "neg_unrealized", "nupl", "peak_regret", "loss_", "net_unrealized")
        if any(m.startswith(p) for p in prof_prefixes): return "Profitability & SOPR"
        if any(k in m for k in ("profit", "loss", "pnl", "sopr", "realized", "capitulation")): return "Profitability & SOPR"

        # 8. Supply & Scarcity
        supply_prefixes = ("supply_", "subsidy_", "inflation_", "circulating_", "illiquid_", "liquid_", 
                           "highly_liquid_", "hodl_", "liveliness", "vaultedness", "cdd_", "coindays_", 
                           "coinblocks_", "cointime_", "thermocap_", "thermo_")
        if any(m.startswith(p) for p in supply_prefixes): return "Supply & Scarcity"
        if any(k in m for k in ("supply", "scarcity", "hodl", "liveliness", "vaultedness", "cointime")): return "Supply & Scarcity"

        # 9. Network Activity
        net_prefixes = ("block_", "blocks_", "tx_", "transaction_", "transactions_", "address_", 
                        "addr_", "fee_", "fees_", "hash_", "hashrate_", "hash_rate_", "sent_", 
                        "received_", "difficulty", "segwit_", "taproot_", "height_", "mempool_", 
                        "vsize_", "weight_", "input_", "inputs_", "output_", "outputs_", 
                        "empty_addr_", "new_addr_", "opreturn_")
        if any(m.startswith(p) for p in net_prefixes): return "Network Activity"
        if any(k in m for k in ("block", "tx_", "transaction", "mempool", "hashrate", "difficulty", "sent")): return "Network Activity"

        # 10. Entities
        entity_patterns = ("_blocks_mined", "_coinbase", "_fee", "_subsidy")
        if any(p in m for p in entity_patterns): return "Entities"
        
        entity_keywords = ("bitcoincom_", "btccom_", "foundry_", "slush_", "antpool_", "f2pool_", "viabtc_") # ... (truncated for space)
        if m.startswith(entity_keywords): return "Entities"

        # 11. Market & Valuation
        val_prefixes = ("market_cap", "realized_cap", "mvrv", "nvt", "investor_", "cost_basis", 
                        "active_", "vaulted_", "true_market", "lower_price", "upper_price", 
                        "greed_", "oracle_", "terminal_", "balanced_", "delta_", "average_cap")
        if any(m.startswith(p) for p in val_prefixes): return "Market & Valuation"
        if any(k in m for k in ("market_cap", "realized_cap", "mvrv", "nvt", "valuation", "velocity")): return "Market & Valuation"

        # 12. Mining
        if any(k in m for k in ("miner_", "mining", "block_reward", "hash_rate", "reward_")): return "Block Reward Distributions"

        return "Other"