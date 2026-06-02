import pandas as pd
import polars as pl


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


def process_cycle_year_by_year(
    cycle: dict,
    btc_data: pl.DataFrame,
    runner,
    dynamic_strategy=None,
    total_budget_usd: float = 1000.0,
    top_buy_quantile: float = 0.90,
) -> dict:
    """Run dynamic strategy vs uniform DCA baseline over a cycle, year by year.

    Pass `dynamic_strategy` to swap the strategy per notebook
    (e.g. SimpleZScoreStrategy(), MomentumStrategy()).
    Defaults to SimpleZScoreStrategy if not provided.
    """
    from stacksats.strategies.stable.signals.simple_zscore import SimpleZScoreStrategy
    from stacksats.strategies.stable.baselines.uniform import UniformStrategy

    if dynamic_strategy is None:
        dynamic_strategy = SimpleZScoreStrategy()

    uniform_strategy  = UniformStrategy()
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

    dynamic_yearly, uniform_yearly = [], []

    for year in range(start_year, end_year + 1):
        dyn = export_one_year(dynamic_strategy, cycle_df, year, runner)
        if dyn is not None:
            dynamic_yearly.append(dyn)
        uni = export_one_year(uniform_strategy, cycle_df, year, runner)
        if uni is not None:
            uniform_yearly.append(uni)

    if not dynamic_yearly:
        raise ValueError(f"No valid dynamic exports for {cycle_label}")
    if not uniform_yearly:
        raise ValueError(f"No valid uniform exports for {cycle_label}")

    dynamic_all = pl.concat(dynamic_yearly).rename({"weight": "dynamic_weight_raw"})
    uniform_all = pl.concat(uniform_yearly).rename({"weight": "baseline_weight_raw"})

    merged = (
        dynamic_all.select(["date", "price_usd", "dynamic_weight_raw"])
        .join(uniform_all.select(["date", "baseline_weight_raw"]), on="date", how="inner")
        .sort("date")
    )

    merged = merged.with_columns([
        (pl.col("dynamic_weight_raw")  / merged["dynamic_weight_raw"].sum()).alias("dynamic_weight"),
        (pl.col("baseline_weight_raw") / merged["baseline_weight_raw"].sum()).alias("baseline_weight"),
    ])
    merged = merged.with_columns([
        (pl.col("dynamic_weight")  * total_budget_usd).alias("dynamic_usd"),
        (pl.col("baseline_weight") * total_budget_usd).alias("baseline_usd"),
    ])
    merged = merged.with_columns([
        (pl.col("dynamic_usd")  / pl.col("price_usd")).alias("btc_accum_dynamic"),
        (pl.col("baseline_usd") / pl.col("price_usd")).alias("btc_accum_baseline"),
    ])
    merged = merged.with_columns([
        (pl.col("btc_accum_dynamic")  * 100_000_000).alias("sats_accum_dynamic"),
        (pl.col("btc_accum_baseline") * 100_000_000).alias("sats_accum_baseline"),
    ])
    merged = merged.with_columns([
        (pl.col("sats_accum_dynamic")  / pl.col("dynamic_usd")).alias("sats_per_dollar_dynamic"),
        (pl.col("sats_accum_baseline") / pl.col("baseline_usd")).alias("sats_per_dollar_baseline"),
    ])

    total_dynamic_btc  = merged["btc_accum_dynamic"].sum()
    total_baseline_btc = merged["btc_accum_baseline"].sum()
    spd_dynamic  = (total_dynamic_btc  / total_budget_usd) * 100_000_000
    spd_baseline = (total_baseline_btc / total_budget_usd) * 100_000_000
    pct_diff     = ((total_dynamic_btc - total_baseline_btc) / total_baseline_btc) * 100

    top_buy_threshold = merged["dynamic_weight"].quantile(top_buy_quantile)
    top_buy_points = (
        merged
        .filter(pl.col("dynamic_weight") >= top_buy_threshold)
        .select(["date", "price_usd", "dynamic_weight"])
        .sort("dynamic_weight", descending=True)
        .to_pandas()
    )
    top_buy_points["date"] = pd.to_datetime(top_buy_points["date"])

    plot_df = merged.to_pandas()
    plot_df["date"] = pd.to_datetime(plot_df["date"])

    return {
        "label": cycle_label, "start": cycle_start, "end": cycle_end,
        "merged": merged, "plot_df": plot_df,
        "top_buy_points": top_buy_points,
        "top_buy_threshold": top_buy_threshold,
        "top_buy_quantile": top_buy_quantile,
        "total_dynamic_btc": total_dynamic_btc,
        "total_baseline_btc": total_baseline_btc,
        "sats_per_dollar_dynamic": spd_dynamic,
        "sats_per_dollar_baseline": spd_baseline,
        "pct_diff_vs_baseline": pct_diff,
        "performance_label": "better" if pct_diff > 0 else "worse",
    }