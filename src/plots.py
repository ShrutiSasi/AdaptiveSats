from dataclasses import dataclass
import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go
from scipy.cluster.hierarchy import dendrogram as _scipy_dendrogram
from plotly.subplots import make_subplots
from .config import HALVING_PERIODS, CALENDAR_CYCLES



# Private module-level aliases so default parameters can fall back to the
# module-level constants even when the parameter name shadows them.
halving_periods = HALVING_PERIODS
calendar_cycles = CALENDAR_CYCLES
_DEFAULT_HALVING_PERIODS = halving_periods
_DEFAULT_CALENDAR_CYCLES = calendar_cycles


@dataclass
class StrategyColumns:
    """Maps logical roles to the actual column names in a strategy plot_df.

    Example
    -------
    cols = StrategyColumns(
        weight="momentum_weight",
        spd="sats_per_dollar_dynamic",
        sats_accum="sats_accum_dynamic",
    )
    """
    weight: str = "dynamic_weight"
    spd: str = "sats_per_dollar_dynamic"
    sats_accum: str = "sats_accum_dynamic"

# ---------------------------------------------------------------------------
# Reusable plot functions
# ---------------------------------------------------------------------------

def plot_dendrogram(
    Z,
    labels: list[str] | None,
    title: str,
    threshold: float | None = None,
    no_labels: bool = False,
    save_path=None,
    show: bool = True,
) -> None:
    """Render a correlation dendrogram.

    Parameters
    ----------
    Z         : linkage matrix from scipy.
    labels    : column labels; ignored when no_labels=True.
    title     : axes title string.
    threshold : if set, draws a red dashed horizontal line at this height.
    no_labels : set True for large dendrograms where labels are unreadable.
    save_path : optional Path to save the figure (300 dpi).
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    _scipy_dendrogram(
        Z,
        labels=None if no_labels else labels,
        leaf_rotation=45,
        leaf_font_size=9,
        ax=ax,
    )
    if no_labels:
        ax.set_xticks([])
    ax.set_title(title, fontsize=13)
    ax.set_xlabel("Feature")
    ax.set_ylabel("Dissimilarity (1 - |Pearson r|)")
    if threshold is not None:
        plt.axhline(y=threshold, color="r", linestyle="--")
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()


def plot_price_history_with_halvings(
    df: pd.DataFrame,
    halvings: list[tuple[str, str]],
    save_path=None,
    show: bool = True,
) -> None:
    """Plot BTC price history on a log scale with halving epoch shading.

    Parameters
    ----------
    df       : pandas DataFrame with columns day_utc (date) and price_usd.
    halvings : list of (label, date_str) tuples, e.g. from config.HALVINGS.
    save_path: optional Path to save the figure.
    """
    halving_dates = [
        (label, datetime.date.fromisoformat(d)) for label, d in halvings
    ]

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df["day_utc"], df["price_usd"],
            color="darkorange", linewidth=1, label="BTC Price (USD)")
    ax.set_yscale("log")

    for label, hdate in halving_dates:
        ax.axvline(hdate, color="steelblue", linestyle="--", linewidth=1.5)
        ax.text(hdate, ax.get_ylim()[1], label,
                rotation=0, ha="center", va="top", fontsize=8, color="steelblue")

    epoch_bounds = [
        datetime.date(2009, 1, 3),
        *[datetime.date.fromisoformat(d) for _, d in halvings],
        df["day_utc"].max(),
    ]
    colors = ["#FFF3CD", "#D4EDDA", "#CCE5FF", "#F8D7DA"]
    epoch_labels = [f"Epoch {i + 1}" for i in range(len(epoch_bounds) - 1)]
    for i in range(len(epoch_bounds) - 1):
        ax.axvspan(epoch_bounds[i], epoch_bounds[i + 1],
                   alpha=0.15, color=colors[i], label=epoch_labels[i])

    ax.set_title("Bitcoin Price History with Halving Epochs (Train Set: 2009–2023)", fontsize=14)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price USD (log scale)")
    ax.legend(fontsize=8)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()


def plot_cycle_violin(
    cycle_df: pd.DataFrame,
    metrics: list[str],
    cycle_order: list[str],
    palette: list[str] | None = None,
    save_path=None,
    show: bool = True,
) -> None:
    """Violin plot of metric distributions across market cycle epochs.

    Parameters
    ----------
    cycle_df    : long DataFrame with columns: metric, value, cycle.
    metrics     : list of metric names to plot (one subplot each).
    cycle_order : ordered list of cycle labels for the x-axis.
    palette     : optional list of colours; defaults to 4-colour set.
    save_path   : optional Path to save the figure.
    """
    if palette is None:
        palette = ["#FFC107", "#28A745", "#007BFF", "#DC3545"]

    nrows = (len(metrics) + 1) // 2
    fig, axes = plt.subplots(nrows, 2, figsize=(16, nrows * 5), sharey=False)

    for ax, metric in zip(axes.flatten(), metrics):
        data = cycle_df[cycle_df["metric"] == metric]
        if data.empty:
            ax.set_title(f"{metric}\n(no data)")
            continue

        present_cycles = [c for c in cycle_order if c in data["cycle"].values]
        sns.violinplot(
            data=data, x="cycle", y="value",
            hue="cycle",
            order=present_cycles,
            palette=palette[: len(present_cycles)],
            ax=ax, inner="quartile", cut=0, legend=False,
        )
        ax.set_title(metric.upper(), fontsize=15)
        ax.set_xlabel("")
        ax.set_ylabel("Value" if metric == metrics[0] else "")
        ax.tick_params(axis="x", labelsize=15)

    # Hide any unused axes
    for ax in axes.flatten()[len(metrics):]:
        ax.set_visible(False)

    fig.suptitle(
        "Metric Distributions Across Market Cycles", fontsize=15
    )
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    if show:
        plt.show()


def assign_cycle_label(date, cycles: list = None) -> str:
    """Return the calendar-cycle label for *date*.

    Parameters
    ----------
    date   : anything convertible to a pandas Timestamp.
    cycles : list of dicts with keys 'label', 'start', 'end'.
             Defaults to the module-level ``calendar_cycles``.
    """
    if cycles is None:
        cycles = _DEFAULT_CALENDAR_CYCLES
    ts = pd.Timestamp(date)
    for c in cycles:
        if pd.Timestamp(c["start"]) <= ts <= pd.Timestamp(c["end"]):
            return c["label"]
    return "Outside defined cycles"


def compute_yearly_top_buys(
    plot_df: pd.DataFrame,
    weight_col: str,
    quantile: float = 0.90,
    min_dca_multiplier: float = 1.0
) -> pd.DataFrame:
    """Rows where strategy weight >= the per-calendar-year quantile threshold.

    Parameters
    ----------
    plot_df    : DataFrame that must have columns 'date', 'price_usd',
                 'year', and ``weight_col``.
    weight_col : column name of the strategy allocation weight.
    quantile   : e.g. 0.90 keeps the top 10 % of days per year.
    min_dca_multiplier: a day is only marked if its weight is meaningfully above uniform DCA

    Returns
    -------
    DataFrame sorted by date with an added 'top_buy_threshold_year' column.
    Returns an empty DataFrame (preserving columns) when input is empty or
    lacks a 'year' column.
    """
    if plot_df.empty or "year" not in plot_df.columns:
        return pd.DataFrame(
            columns=list(plot_df.columns) + ["top_buy_threshold_year"]
        )

    groups = []
    for _, grp in plot_df.groupby("year", sort=False):
        dca_w = 1.0 / len(grp)
        threshold = max(grp[weight_col].quantile(quantile), min_dca_multiplier * dca_w)
        top = grp[grp[weight_col] >= threshold].copy()
        top["top_buy_threshold_year"] = threshold
        groups.append(top)

    if not groups:
        return pd.DataFrame(
            columns=list(plot_df.columns) + ["top_buy_threshold_year"]
        )

    return pd.concat(groups).sort_values("date").reset_index(drop=True)


def plot_strategy_full_period(
    plot_df: pd.DataFrame,
    cols: StrategyColumns,
    strategy_name: str,
    date_range: tuple,
    halving_periods: list = None,
    cycles: list = None,
    top_buy_quantile: float = 0.90,
    min_dca_multiplier: float = 1.0,
    test_start_date: str | None = None, 
    width: int = 1450,
    height: int = 780,
    show: bool = True,
) -> go.Figure:
    """One Plotly chart covering the full date range.

    Required columns in plot_df
    ---------------------------
    date, price_usd, baseline_weight, sats_per_dollar_baseline,
    sats_accum_baseline, and all three columns named in ``cols``.

    Parameters
    ----------
    cols          : StrategyColumns with weight / spd / sats_accum column names.
    date_range    : (start_str, end_str) for the x-axis, e.g. ("2010-08-16", "2023-12-31").
    halving_periods: override the module-level list if needed.
    cycles        : override the module-level calendar_cycles; cycle boundary
                    vlines are drawn using this list.  Pass [] to suppress vlines.
    top_buy_quantile: e.g. 0.90 marks the top 10 % of days per calendar year.
    """
    if halving_periods is None:
        halving_periods = _DEFAULT_HALVING_PERIODS
    if cycles is None:
        cycles = _DEFAULT_CALENDAR_CYCLES

    df = _ensure_year_cycle_cols(plot_df, cycles)
    top_buys = compute_yearly_top_buys(df, cols.weight, top_buy_quantile, min_dca_multiplier)

    # spd_d = _compute_spd(df, cols.weight)
    # spd_b = _compute_spd(df, "baseline_weight")
    # pct   = (spd_d - spd_b) / spd_b * 100 if spd_b else 0.0
    pct_n = int(round((1 - top_buy_quantile) * 100))
    y0    = pd.Timestamp(date_range[0]).year
    y1    = pd.Timestamp(date_range[1]).year

    # if pct > 0:
    #     perf_text = (
    #         f"<span style='color:green;'>"
    #         f"▲ {pct:+.2f}% vs DCA"
    #         f"</span>"
    #     )
    # else:
    #     perf_text = (
    #         f"<span style='color:red;'>"
    #         f"▼ {pct:+.2f}% vs DCA"
    #         f"</span>"
    #     )
    
    # title = (
    #     f"<b>{strategy_name} vs Baseline DCA  {y0}–{y1}</b><br>"
    #     f"Top {pct_n}% Buy Days Per Calendar Year  |  "
    #     f"{strategy_name} SPD: {spd_d:,.0f}  |  "
    #     f"DCA SPD: {spd_b:,.0f}  |  "
    #     f"{perf_text}"
    # )

    def _pct_span(pct: float) -> str:
            color = "green" if pct >= 0 else "red"
            arrow = "▲" if pct >= 0 else "▼"
            return f"<span style='color:{color};'>{arrow} {pct:+.2f}% vs DCA</span>"
    
    if test_start_date is not None:
        ts       = pd.Timestamp(test_start_date)
        train_df = df[df["date"] < ts]
        test_df  = df[df["date"] >= ts]

        spd_d_tr = _compute_spd(train_df, cols.weight)
        spd_b_tr = _compute_spd(train_df, "baseline_weight")
        pct_tr   = (spd_d_tr - spd_b_tr) / spd_b_tr * 100 if spd_b_tr else 0.0

        spd_d_te = _compute_spd(test_df, cols.weight)
        spd_b_te = _compute_spd(test_df, "baseline_weight")
        pct_te   = (spd_d_te - spd_b_te) / spd_b_te * 100 if spd_b_te else 0.0
      
        title = (
            f"<b>{strategy_name} vs Baseline DCA  {y0}–{y1}</b>"
            f"  (Top {pct_n}% Buy Days / Year)<br>"
            f"Train ({y0}–{(ts - pd.Timedelta(days=1)).year}): "
            f"{strategy_name} SPD: {spd_d_tr:,.0f}  |  DCA SPD: {spd_b_tr:,.0f}  | {_pct_span(pct_tr)} <br>"
            f"Test ({ts.year}–{y1}): "
            f"{strategy_name} SPD: {spd_d_te:,.0f}  |  DCA SPD: {spd_b_te:,.0f}  |  {_pct_span(pct_te)}"
        )
    else:
        spd_d = _compute_spd(df, cols.weight)
        spd_b = _compute_spd(df, "baseline_weight")
        pct   = (spd_d - spd_b) / spd_b * 100 if spd_b else 0.0
        perf_text = (
            f"<span style='color:green;'> {_pct_span(pct)}</span>"
            if pct > 0 else
            f"<span style='color:red;'> {_pct_span(pct)}</span>"
        )
        title = (
            f"<b>{strategy_name} vs Baseline DCA  {y0}–{y1}</b><br>"
            f"Top {pct_n}% Buy Days Per Calendar Year  |  "
            f"{strategy_name} SPD: {spd_d:,.0f}  |  "
            f"DCA SPD: {spd_b:,.0f}  |  "
            f"{perf_text}"
        )

    fig = _build_strategy_fig(
        plot_df=df, top_buy_points=top_buys,
        cols=cols, strategy_name=strategy_name,
        title=title, date_range=date_range,
        halving_periods=halving_periods, cycles=cycles,
        width=width, height=height,
    )

    if test_start_date is not None:
        x_ms = pd.Timestamp(test_start_date).value // 10**6  # nanoseconds → milliseconds
        fig.add_vline(
            x=x_ms,
            line_width=2, line_dash="dash", line_color="royalblue",
            annotation_text="Test starts",
            annotation_position="top right",
            annotation_font=dict(size=11, color="royalblue"),
        )
        fig.update_layout(margin=dict(t=180))

    if show:
        fig.show()
    return fig


def plot_strategy_by_cycle(
    plot_df: pd.DataFrame,
    cols: StrategyColumns,
    strategy_name: str,
    halving_periods: list = None,
    cycles: list = None,
    top_buy_quantile: float = 0.90,
    min_dca_multiplier: float = 1.0,
    width: int = 1350,
    height_per_row: int = 550,
    show: bool = True,
) -> go.Figure:
    """Faceted figure: one subplot row per calendar cycle (single column).

    Returns a single go.Figure.
    """
    if halving_periods is None:
        halving_periods = _DEFAULT_HALVING_PERIODS
    if cycles is None:
        cycles = _DEFAULT_CALENDAR_CYCLES

    df = _ensure_year_cycle_cols(plot_df, cycles)

    cycle_slices = []
    for cycle in cycles:
        c_start = pd.Timestamp(cycle["start"])
        c_end   = pd.Timestamp(cycle["end"])
        slice_df = df[(df["date"] >= c_start) & (df["date"] <= c_end)].copy()
        if not slice_df.empty:
            cycle_slices.append((cycle, slice_df))

    n = len(cycle_slices)
    if n == 0:
        raise ValueError("No cycle data found in plot_df.")

    pct_n = int(round((1 - top_buy_quantile) * 100))
    top_buy_label = f"Top {pct_n}% Buy Days"

    # Pre-compute per-cycle stats for subplot titles
    subplot_titles = []
    for cycle, slice_df in cycle_slices:
        spd_d    = _compute_spd(slice_df, cols.weight)
        spd_b    = _compute_spd(slice_df, "baseline_weight")
        pct_diff = (spd_d - spd_b) / spd_b * 100 if spd_b else 0.0
        if pct_diff > 0:
            perf_text = (
                f"<span style='color:green;'>"
                f"▲ {pct_diff:+.2f}% vs DCA"
                f"</span>"
            )
        else:
            perf_text = (
                f"<span style='color:red;'>"
                f"▼ {pct_diff:+.2f}% vs DCA"
                f"</span>"
            )
        threshold      = slice_df[cols.weight].quantile(top_buy_quantile)
        subplot_titles.append(
            f"<b>{cycle['label']} | {strategy_name} Strategy vs Baseline DCA</b><br>"
            f"{strategy_name} SPD: {spd_d:.0f} | DCA SPD: {spd_b:.0f} | "
            f"{perf_text} | "
            f"Top buy threshold: {threshold:.8f} <br>"
        )

    fig = make_subplots(
        rows=n, cols=1,
        specs=[[{"secondary_y": True}]] * n,
        subplot_titles=subplot_titles,
        shared_xaxes=False,
        vertical_spacing=0.05,
    )

    for i, (cycle, slice_df) in enumerate(cycle_slices, start=1):
        c_start  = pd.Timestamp(cycle["start"])
        c_end    = pd.Timestamp(cycle["end"])
        top_buys = compute_yearly_top_buys(slice_df, cols.weight, top_buy_quantile, min_dca_multiplier)

        x_ref = f"x{i}" if i > 1 else "x"
        y_idx = 2 * (i - 1) + 1
        y_ref = f"y{y_idx} domain" if y_idx > 1 else "y domain"

        # Halving shading with annotation labels, clipped to this cycle        
        for period in halving_periods:
            shaded_start = max(pd.Timestamp(period["start"]), c_start)
            shaded_end   = min(pd.Timestamp(period["end"]),   c_end)
            if shaded_start <= shaded_end:
                fig.add_shape(
                    type="rect",
                    xref=x_ref, yref=y_ref,
                    x0=shaded_start, x1=shaded_end,
                    y0=0, y1=1,
                    fillcolor=period["color"],
                    opacity=1.0,
                    layer="below",
                    line_width=0,
                )
                fig.add_annotation(
                    x=shaded_start, y=0.97,
                    xref=x_ref, yref=y_ref,
                    text=period["label"],
                    showarrow=False,
                    xanchor="left", yanchor="top",
                    font=dict(size=10),
                )

        _add_strategy_subplot_traces(
            fig, row=i, col=1,
            plot_df=slice_df, top_buy_points=top_buys,
            cols=cols, strategy_name=strategy_name,
            show_legend=(i == 1),
            top_buy_label=top_buy_label,
        )

        fig.update_xaxes(title_text="Date", range=[c_start, c_end], showgrid=True,
                         row=i, col=1)
        fig.update_yaxes(title_text="BTC Price (USD, log scale)", type="log",
                         tickprefix="$", showgrid=True,
                         row=i, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Allocation Weight", showgrid=False,
                         row=i, col=1, secondary_y=True)

    fig.update_layout(
        width=width,
        height=n * height_per_row + 80,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="left", x=0),
        margin=dict(l=70, r=70, t=80, b=60),
        template="plotly_white",
    )
    if show:
        fig.show()
    return fig


def plot_strategy_by_year(
    plot_df: pd.DataFrame,
    cols: StrategyColumns,
    strategy_name: str,
    years: list = None,
    halving_periods: list = None,
    top_buy_quantile: float = 0.90,
    min_dca_multiplier: float = 1.0,
    width: int = 1450,
    height_per_row: int = 380,
    show: bool = True,
) -> go.Figure:
    """Faceted figure: two-column grid, one subplot per calendar year.

    Returns a single go.Figure.
    """
    if halving_periods is None:
        halving_periods = _DEFAULT_HALVING_PERIODS

    df = _ensure_year_cycle_cols(plot_df)

    if years is None:
        years = sorted(df["year"].unique())

    year_slices = []
    for year in years:
        year_df = df[df["year"] == year].copy()
        if not year_df.empty:
            year_slices.append((year, year_df))

    n_years = len(year_slices)
    if n_years == 0:
        raise ValueError("No year data found in plot_df.")

    n_cols = 2
    n_rows = (n_years + 1) // 2
    pct_n  = int(round((1 - top_buy_quantile) * 100))

    # Flat list left-to-right, top-to-bottom; pad to even length if needed
    subplot_titles = []
    for year, year_df in year_slices:
        spd_d = _compute_spd(year_df, cols.weight)
        spd_b = _compute_spd(year_df, "baseline_weight")
        pct   = (spd_d - spd_b) / spd_b * 100 if spd_b else 0.0
        if pct > 0:
            perf_text = (
                f"<span style='color:green;'>"
                f"▲ {pct:+.2f}% vs DCA"
                f"</span>"
            )
        else:
            perf_text = (
                f"<span style='color:red;'>"
                f"▼ {pct:+.2f}% vs DCA"
                f"</span>"
            )
        subplot_titles.append(
            f"<sup>{year}  |  "
            f"{strategy_name} SPD: {spd_d:,.0f}  |  DCA SPD: {spd_b:,.0f}  |  {perf_text}</sup>"
        )
    if n_years % 2 != 0:
        subplot_titles.append("")  # empty slot for the last cell

    specs = [[{"secondary_y": True}, {"secondary_y": True}] for _ in range(n_rows)]

    fig = make_subplots(
        rows=n_rows, cols=n_cols,
        specs=specs,
        subplot_titles=subplot_titles,
        shared_xaxes=False,
        vertical_spacing=0.04,
        horizontal_spacing=0.06,
    )

    for idx, (year, year_df) in enumerate(year_slices):
        row = idx // n_cols + 1
        col = idx % n_cols + 1
        y_start  = pd.Timestamp(f"{year}-01-01")
        y_end    = pd.Timestamp(f"{year}-12-31")
        top_buys = compute_yearly_top_buys(year_df, cols.weight, top_buy_quantile, min_dca_multiplier)

        # Halving shading clipped to this year (usually empty, visible near halvings)
        for period in halving_periods:
            shaded_start = max(pd.Timestamp(period["start"]), y_start)
            shaded_end   = min(pd.Timestamp(period["end"]),   y_end)
            if shaded_start <= shaded_end:
                fig.add_vrect(
                    x0=shaded_start, x1=shaded_end,
                    fillcolor=period["color"], opacity=1.0,
                    layer="below", line_width=0,
                    row=row, col=col,
                )

        _add_strategy_subplot_traces(
            fig, row=row, col=col,
            plot_df=year_df, top_buy_points=top_buys,
            cols=cols, strategy_name=strategy_name,
            show_legend=(idx == 0),
        )

        fig.update_xaxes(range=[y_start, y_end], row=row, col=col)
        fig.update_yaxes(type="log", tickprefix="$", showgrid=True,
                         row=row, col=col, secondary_y=False)
        fig.update_yaxes(showgrid=False, row=row, col=col, secondary_y=True)
        fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
        fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True, secondary_y=False)
        fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True, secondary_y=True)

    fig.update_layout(
        title=dict(text=f"<b>{strategy_name} vs Baseline DCA — by Year</b>",
                   x=0.5, font=dict(size=16)),
        width=width,
        height=n_rows * height_per_row + 80,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        margin=dict(l=70, r=70, t=100, b=60),
        template="plotly_white",
    )
    if show:
        fig.show()
    return fig

# -- private helpers ---------------------------------------------------------

def _ensure_year_cycle_cols(
    plot_df: pd.DataFrame,
    cycles: list = None,
) -> pd.DataFrame:
    """Return a copy of plot_df with 'year' and 'cycle_label' columns added."""
    df = plot_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    if "year" not in df.columns:
        df["year"] = df["date"].dt.year
    if "cycle_label" not in df.columns:
        df["cycle_label"] = df["date"].apply(
            lambda d: assign_cycle_label(d, cycles)
        )
    return df


def _compute_spd(df: pd.DataFrame, weight_col: str) -> float:
    """Weighted-average sats per dollar: sum(w / price) / sum(w) * 1e8."""
    total_w = df[weight_col].sum()
    if total_w == 0:
        return 0.0
    return (df[weight_col] / df["price_usd"]).sum() / total_w * 1e8


def _build_strategy_fig(
    plot_df: pd.DataFrame,
    top_buy_points: pd.DataFrame,
    cols: StrategyColumns,
    strategy_name: str,
    title: str,
    date_range: tuple,
    halving_periods: list = None,
    cycles: list = None,
    width: int = 1450,
    height: int = 780,
) -> go.Figure:
    """Build and return a Plotly strategy-vs-DCA figure.

    Parameters
    ----------
    plot_df       : filtered pandas DataFrame for the time window.
    top_buy_points: output of compute_yearly_top_buys().
    cols          : StrategyColumns instance.
    strategy_name : display name, e.g. "Momentum".
    title         : fully formatted HTML title string.
    date_range    : (start_str, end_str) for xaxis clipping.
    halving_periods: list of halving dicts; defaults to module-level constant.
    cycles        : list of calendar-cycle dicts for vlines; pass None to skip.
    width, height : figure size in pixels.
    """
    if halving_periods is None:
        halving_periods = _DEFAULT_HALVING_PERIODS

    range_start = pd.Timestamp(date_range[0])
    range_end   = pd.Timestamp(date_range[1])

    fig = go.Figure()

    # 1 — Halving-period background shading, clipped to the window
    for period in halving_periods:
        shaded_start = max(pd.Timestamp(period["start"]), range_start)
        shaded_end   = min(pd.Timestamp(period["end"]),   range_end)
        if shaded_start <= shaded_end:
            fig.add_vrect(
                x0=shaded_start, x1=shaded_end,
                fillcolor=period["color"], opacity=1.0,
                layer="below", line_width=0,
                annotation_text=period["label"],
                annotation_position="top left",
                annotation_font_size=11,
            )

    # 2 — Calendar-cycle boundary vlines (suppressed for per-cycle/year charts)
    if cycles is not None:
        for cycle in cycles:
            fig.add_vline(
                x=pd.Timestamp(cycle["start"]),
                line_width=1, line_dash="dot", line_color="gray",
            )

    # 3 — BTC price line (left y-axis, log scale)
    fig.add_trace(go.Scatter(
        x=plot_df["date"],
        y=plot_df["price_usd"],
        mode="lines",
        name="BTC Price (USD)",
        line=dict(color="black", width=2),
        yaxis="y1",
        customdata=plot_df[[
            "year", "cycle_label",
            cols.weight, "baseline_weight",
            cols.spd, "sats_per_dollar_baseline",
            cols.sats_accum, "sats_accum_baseline",
        ]],
        hovertemplate=(
            "<b>Date</b>: %{x|%Y-%m-%d}<br>"
            "<b>Year</b>: %{customdata[0]}<br>"
            "<b>Cycle</b>: %{customdata[1]}<br>"
            "<b>BTC Price</b>: $%{y:,.2f}<br>"
            f"<b>{strategy_name} Weight</b>: %{{customdata[2]:.8f}}<br>"
            "<b>DCA Weight</b>: %{customdata[3]:.8f}<br>"
            f"<b>{strategy_name} sats/$</b>: %{{customdata[4]:,.2f}}<br>"
            "<b>DCA sats/$</b>: %{customdata[5]:,.2f}<br>"
            f"<b>{strategy_name} sats accum.</b>: %{{customdata[6]:,.2f}}<br>"
            "<b>DCA sats accum.</b>: %{customdata[7]:,.2f}"
            "<extra></extra>"
        ),
    ))

    # 4 — Strategy weight (right y-axis, green area fill)
    fig.add_trace(go.Scatter(
        x=plot_df["date"],
        y=plot_df[cols.weight],
        mode="lines",
        name=f"{strategy_name} Weight",
        line=dict(color="green", width=1.5),
        fill="tozeroy", fillcolor="rgba(0, 128, 0, 0.35)",
        yaxis="y2",
        customdata=plot_df[[
            "year", "cycle_label",
            "price_usd", cols.spd, cols.sats_accum,
        ]],
        hovertemplate=(
            "<b>Date</b>: %{x|%Y-%m-%d}<br>"
            "<b>Year</b>: %{customdata[0]}<br>"
            "<b>Cycle</b>: %{customdata[1]}<br>"
            f"<b>{strategy_name} Weight</b>: %{{y:.8f}}<br>"
            "<b>BTC Price</b>: $%{customdata[2]:,.2f}<br>"
            f"<b>{strategy_name} sats/$</b>: %{{customdata[3]:,.2f}}<br>"
            f"<b>{strategy_name} sats accum.</b>: %{{customdata[4]:,.2f}}"
            "<extra></extra>"
        ),
    ))

    # 5 — Baseline DCA weight (right y-axis, orange dashed)
    fig.add_trace(go.Scatter(
        x=plot_df["date"],
        y=plot_df["baseline_weight"],
        mode="lines",
        name="Baseline DCA Weight",
        line=dict(color="orange", width=2, dash="dash"),
        yaxis="y2",
        customdata=plot_df[[
            "year", "cycle_label",
            "price_usd", "sats_per_dollar_baseline", "sats_accum_baseline",
        ]],
        hovertemplate=(
            "<b>Date</b>: %{x|%Y-%m-%d}<br>"
            "<b>Year</b>: %{customdata[0]}<br>"
            "<b>Cycle</b>: %{customdata[1]}<br>"
            "<b>DCA Weight</b>: %{y:.8f}<br>"
            "<b>BTC Price</b>: $%{customdata[2]:,.2f}<br>"
            "<b>DCA sats/$</b>: %{customdata[3]:,.2f}<br>"
            "<b>DCA sats accum.</b>: %{customdata[4]:,.2f}"
            "<extra></extra>"
        ),
    ))

    # 6 — Top-buy markers (left y-axis, green triangle-up)
    if not top_buy_points.empty:
        fig.add_trace(go.Scatter(
            x=top_buy_points["date"],
            y=top_buy_points["price_usd"],
            mode="markers",
            name="Top Buy Days",
            marker=dict(
                color="green", symbol="triangle-up", size=8,
                line=dict(color="black", width=1),
            ),
            yaxis="y1",
            customdata=top_buy_points[[
                "year", cols.weight, "top_buy_threshold_year",
            ]],
            hovertemplate=(
                "<b>Top Buy Date</b>: %{x|%Y-%m-%d}<br>"
                "<b>Year</b>: %{customdata[0]}<br>"
                "<b>BTC Price</b>: $%{y:,.2f}<br>"
                f"<b>{strategy_name} Weight</b>: %{{customdata[1]:.8f}}<br>"
                "<b>Year Threshold</b>: %{customdata[2]:.8f}"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=15)),
        width=width, height=height,
        hovermode="x unified",
        xaxis=dict(title="Date", range=[range_start, range_end], showgrid=True),
        yaxis=dict(
            title="BTC Price (USD, log scale)",
            type="log", side="left",
            showgrid=True, tickprefix="$",
        ),
        yaxis2=dict(
            title="Allocation Weight",
            overlaying="y", side="right", showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
        margin=dict(l=70, r=70, t=130, b=60),
        template="plotly_white",
    )

    return fig


def _add_strategy_subplot_traces(
    fig: go.Figure,
    row: int,
    col: int,
    plot_df: pd.DataFrame,
    top_buy_points: pd.DataFrame,
    cols: StrategyColumns,
    strategy_name: str,
    show_legend: bool,
    top_buy_label: str = "Top Buy Days",
) -> None:
    """Add the four standard strategy traces to one subplot cell."""
    # BTC price — primary y (log)
    fig.add_trace(go.Scatter(
        x=plot_df["date"], y=plot_df["price_usd"],
        mode="lines", name="BTC Price (USD)",
        line=dict(color="black", width=1.5),
        showlegend=show_legend,
        customdata=plot_df[[
            cols.weight, "baseline_weight",
            cols.spd, "sats_per_dollar_baseline",
            cols.sats_accum, "sats_accum_baseline",
        ]],
        hovertemplate=(
            "<b>Date</b>: %{x|%Y-%m-%d}<br>"
            "<b>BTC Price</b>: $%{y:,.2f}<br>"
            f"<b>{strategy_name} Weight</b>: %{{customdata[0]:.8f}}<br>"
            "<b>DCA Weight</b>: %{customdata[1]:.8f}<br>"
            f"<b>{strategy_name} sats/$</b>: %{{customdata[2]:,.2f}}<br>"
            "<b>DCA sats/$</b>: %{customdata[3]:,.2f}<br>"
            f"<b>{strategy_name} sats accumulated</b>: %{{customdata[4]:,.2f}}<br>"
            "<b>DCA sats accumulated</b>: %{customdata[5]:,.2f}"
            "<extra></extra>"
        ),
    ), row=row, col=col, secondary_y=False)

    # Strategy weight area — secondary y
    fig.add_trace(go.Scatter(
        x=plot_df["date"], y=plot_df[cols.weight],
        mode="lines", name=f"{strategy_name} Weight",
        line=dict(color="green", width=1.2),
        fill="tozeroy", fillcolor="rgba(0,128,0,0.25)",
        showlegend=show_legend,
        customdata=plot_df[["price_usd", cols.spd, cols.sats_accum]],
        hovertemplate=(
            "<b>Date</b>: %{x|%Y-%m-%d}<br>"
            f"<b>{strategy_name} Weight</b>: %{{y:.8f}}<br>"
            "<b>BTC Price</b>: $%{customdata[0]:,.2f}<br>"
            f"<b>{strategy_name} sats/$</b>: %{{customdata[1]:,.2f}}<br>"
            f"<b>{strategy_name} sats accumulated</b>: %{{customdata[2]:,.2f}}"
            "<extra></extra>"
        ),
    ), row=row, col=col, secondary_y=True)

    # Baseline DCA — secondary y, dashed orange
    fig.add_trace(go.Scatter(
        x=plot_df["date"], y=plot_df["baseline_weight"],
        mode="lines", name="Baseline DCA Weight",
        line=dict(color="orange", width=1.5, dash="dash"),
        showlegend=show_legend,
        customdata=plot_df[["price_usd", "sats_per_dollar_baseline", "sats_accum_baseline"]],
        hovertemplate=(
            "<b>Date</b>: %{x|%Y-%m-%d}<br>"
            "<b>DCA Weight</b>: %{y:.8f}<br>"
            "<b>BTC Price</b>: $%{customdata[0]:,.2f}<br>"
            "<b>DCA sats/$</b>: %{customdata[1]:,.2f}<br>"
            "<b>DCA sats accumulated</b>: %{customdata[2]:,.2f}"
            "<extra></extra>"
        ),
    ), row=row, col=col, secondary_y=True)

    # Top-buy markers — primary y
    if not top_buy_points.empty:
        fig.add_trace(go.Scatter(
            x=top_buy_points["date"], y=top_buy_points["price_usd"],
            mode="markers", name=top_buy_label,
            marker=dict(color="green", symbol="triangle-up", size=7,
                        line=dict(color="black", width=1)),
            showlegend=show_legend,
            customdata=top_buy_points[[cols.weight]],
            hovertemplate=(
                "<b>Top Buy Date</b>: %{x|%Y-%m-%d}<br>"
                "<b>BTC Price</b>: $%{y:,.2f}<br>"
                f"<b>{strategy_name} Weight</b>: %{{customdata[0]:.8f}}"
                "<extra></extra>"
            ),
        ), row=row, col=col, secondary_y=False)