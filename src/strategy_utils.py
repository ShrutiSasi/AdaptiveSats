import pandas as pd
import polars as pl
from src import config as _config


def export_one_year(
    strategy,
    btc_data: pl.DataFrame,
    year: int,
    runner,
) -> pl.DataFrame | None:
    """Export strategy weights for a single calendar year."""
    from stacksats.runner.core import ExportConfig

    year_start = f"{year}-01-01"
    year_end   = f"{year}-12-31"

    year_df = (
        btc_data
        .filter(
            (pl.col("date") >= pl.datetime(year, 1, 1)) &
            (pl.col("date") <= pl.datetime(year, 12, 31))
        )
        .sort("date")
    )

    if year_df.is_empty():
        print(f"{year}: skipped, no data")
        return None
    if year_df.height < 365:
        print(f"{year}: skipped, less than 365 rows")
        return None

    try:
        cfg = ExportConfig(range_start=year_start, range_end=year_end)
        export_obj = runner.export(strategy, cfg, btc_df=year_df)
        df = export_obj.to_dataframe()

        df = df.with_columns([
            pl.col("start_date").cast(pl.Datetime),
            pl.col("end_date").cast(pl.Datetime),
            pl.col("date").cast(pl.Datetime),
        ])
        latest_end = df.select(pl.col("end_date").max()).item()
        df_one = df.filter(pl.col("end_date") == latest_end).sort("date")

        print(f"{year}: exported {df_one.height} rows")
        return df_one

    except Exception as e:
        print(f"{year}: skipped due to error -> {e}")
        return None


def run_year_by_year(
    strategies: dict,
    btc_data: pl.DataFrame,
    years,
    runner,
    total_budget_usd: float | None = None,
) -> pl.DataFrame:
    """Export N strategies year-by-year and compute the full weight→sats pipeline.

    Parameters
    ----------
    strategies:
        Ordered mapping of name → strategy instance.
        The first entry's DataFrame supplies ``price_usd``.
        e.g. {"dynamic": MyStrategy(), "mvrv": MVRVStrategy(), "baseline": UniformStrategy()}
    btc_data:
        BTC DataFrame for the relevant range (train or test).
    years:
        Iterable of integer years, e.g. ``range(2018, 2024)``.
    runner:
        StrategyRunner instance.
    total_budget_usd:
        Annual USD budget. Defaults to ``config.TOTAL_BUDGET_USD``.

    Returns
    -------
    pl.DataFrame with shared columns ``date``, ``price_usd``, ``year``
    and per-strategy columns for each name:
        ``{name}_weight_raw``, ``{name}_weight``, ``{name}_usd``,
        ``btc_accum_{name}``, ``sats_accum_{name}``, ``sats_per_dollar_{name}``
    """
    if total_budget_usd is None:
        total_budget_usd = _config.TOTAL_BUDGET_USD

    yearly_by_name: dict[str, list[pl.DataFrame]] = {name: [] for name in strategies}

    for year in years:
        for name, strategy in strategies.items():
            result = export_one_year(strategy, btc_data, year, runner)
            if result is not None:
                yearly_by_name[name].append(result)

    for name, yearly in yearly_by_name.items():
        if not yearly:
            raise ValueError(f"No valid exports for strategy '{name}'")

    # First strategy provides price_usd; subsequent strategies join on date only
    first_name = next(iter(strategies))
    first_df = pl.concat(yearly_by_name[first_name]).rename({"weight": f"{first_name}_weight_raw"})
    merged = first_df.select(["date", "price_usd", f"{first_name}_weight_raw"]).sort("date")

    for name in list(strategies.keys())[1:]:
        other_df = pl.concat(yearly_by_name[name]).rename({"weight": f"{name}_weight_raw"})
        merged = merged.join(other_df.select(["date", f"{name}_weight_raw"]), on="date", how="inner")

    merged = merged.with_columns(pl.col("date").dt.year().alias("year"))

    # Year-normalize raw weights
    merged = merged.with_columns([
        (pl.col(f"{name}_weight_raw") / pl.col(f"{name}_weight_raw").sum().over("year"))
        .alias(f"{name}_weight")
        for name in strategies
    ])
    # weight → USD
    merged = merged.with_columns([
        (pl.col(f"{name}_weight") * total_budget_usd).alias(f"{name}_usd")
        for name in strategies
    ])
    # USD → BTC
    merged = merged.with_columns([
        (pl.col(f"{name}_usd") / pl.col("price_usd")).alias(f"btc_accum_{name}")
        for name in strategies
    ])
    # BTC → sats
    merged = merged.with_columns([
        (pl.col(f"btc_accum_{name}") * _config.SATS_PER_BTC).alias(f"sats_accum_{name}")
        for name in strategies
    ])
    # sats → sats-per-dollar
    merged = merged.with_columns([
        (pl.col(f"sats_accum_{name}") / pl.col(f"{name}_usd")).alias(f"sats_per_dollar_{name}")
        for name in strategies
    ])

    return merged


def compute_performance_summary(
    merged_df: pl.DataFrame,
    strategy_name: str,
    baseline_name: str,
    total_budget_usd: float | None = None,
) -> dict:
    """Compute aggregate performance metrics from a ``run_year_by_year`` result.

    Parameters
    ----------
    merged_df:
        DataFrame returned by ``run_year_by_year``.
    strategy_name:
        The strategy name key used in ``run_year_by_year`` (e.g. ``"dynamic"``).
    baseline_name:
        The baseline name key (e.g. ``"baseline"``).
    total_budget_usd:
        Annual USD budget. Defaults to ``config.TOTAL_BUDGET_USD``.

    Returns
    -------
    dict with keys:
        ``total_{strategy_name}_btc``, ``total_{baseline_name}_btc``,
        ``sats_per_dollar_{strategy_name}``, ``sats_per_dollar_{baseline_name}``,
        ``pct_diff_vs_baseline``, ``performance_label``.
    """
    if total_budget_usd is None:
        total_budget_usd = _config.TOTAL_BUDGET_USD

    total_strat_btc    = merged_df[f"btc_accum_{strategy_name}"].sum()
    total_baseline_btc = merged_df[f"btc_accum_{baseline_name}"].sum()
    num_years          = merged_df["year"].n_unique()
    total_invested     = total_budget_usd * num_years

    spd_strategy = (total_strat_btc    / total_invested) * _config.SATS_PER_BTC
    spd_baseline = (total_baseline_btc / total_invested) * _config.SATS_PER_BTC
    pct_diff     = (total_strat_btc - total_baseline_btc) / total_baseline_btc * 100

    return {
        f"total_{strategy_name}_btc":       total_strat_btc,
        f"total_{baseline_name}_btc":       total_baseline_btc,
        f"sats_per_dollar_{strategy_name}": spd_strategy,
        f"sats_per_dollar_{baseline_name}": spd_baseline,
        "pct_diff_vs_baseline":             pct_diff,
        "performance_label":                "better" if pct_diff > 0 else "worse",
    }


def process_cycle_year_by_year(
    cycle: dict,
    btc_data: pl.DataFrame,
    runner,
    dynamic_strategy=None,
    total_budget_usd: float | None = None,
    top_buy_quantile: float | None = None,
) -> dict:
    """Run dynamic strategy vs uniform DCA baseline over a cycle, year by year.

    Pass ``dynamic_strategy`` to swap the strategy per notebook.
    Defaults to UniformStrategy if not provided.
    Return dict is unchanged from prior version (backward compatible).
    """
    from stacksats.strategies.stable.baselines.uniform import UniformStrategy

    if dynamic_strategy is None:
        dynamic_strategy = UniformStrategy()
    if total_budget_usd is None:
        total_budget_usd = _config.TOTAL_BUDGET_USD
    if top_buy_quantile is None:
        top_buy_quantile = _config.TOP_BUY_QUANTILE

    cycle_label = cycle["label"]
    cycle_start = cycle["start"]
    cycle_end   = cycle["end"]
    start_year  = int(cycle_start[:4])
    end_year    = int(cycle_end[:4])

    print(f"\nProcessing {cycle_label}")

    cycle_df = (
        btc_data
        .filter(
            (pl.col("date") >= pl.lit(cycle_start).str.to_datetime()) &
            (pl.col("date") <= pl.lit(cycle_end).str.to_datetime())
        )
        .sort("date")
    )

    print(cycle_df.select(
        pl.col("date").min().alias("min_date"),
        pl.col("date").max().alias("max_date"),
        pl.len().alias("rows"),
    ))

    strategies = {"dynamic": dynamic_strategy, "baseline": UniformStrategy()}
    merged = run_year_by_year(strategies, cycle_df, range(start_year, end_year + 1), runner, total_budget_usd)
    perf   = compute_performance_summary(merged, "dynamic", "baseline", total_budget_usd)

    plot_df = merged.to_pandas()
    plot_df["date"] = pd.to_datetime(plot_df["date"])
    plot_df["year"] = plot_df["date"].dt.year

    top_buy_points_list = []
    threshold = None
    for year, year_df in plot_df.groupby("year"):
        threshold = year_df["dynamic_weight"].quantile(top_buy_quantile)
        top_year_df = year_df[year_df["dynamic_weight"] >= threshold].copy()
        top_year_df["top_buy_threshold_year"] = threshold
        top_buy_points_list.append(top_year_df)

    top_buy_points = pd.concat(top_buy_points_list, ignore_index=True)
    top_buy_points = top_buy_points.sort_values(["year", "dynamic_weight"], ascending=[True, False])

    return {
        "label": cycle_label, "start": cycle_start, "end": cycle_end,
        "merged": merged, "plot_df": plot_df,
        "top_buy_points": top_buy_points,
        "top_buy_threshold": threshold,
        "top_buy_quantile": top_buy_quantile,
        **perf,
    }