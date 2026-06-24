# AdaptiveSats

![Python 3.11](https://img.shields.io/badge/python-3.11-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![conda](https://img.shields.io/badge/env-conda-brightgreen)

The challenge of investing in Bitcoin is simple to describe but difficult to solve: if you have a fixed amount of money to invest over time, can you consistently buy more Bitcoin by adjusting your purchases based on market conditions, rather than investing the same amount every day?
> **Can adaptive allocation beat naive Dollar-Cost Averaging for long-term Bitcoin accumulation?**

AdaptiveSats is a Python-based research platform built in partnership with the **Trilemma Foundation** (UBC DSCI591 Capstone, 2025–2026) to answer that question. Instead of focusing on Bitcoin's price in dollars, it focuses on maximizing the amount of Bitcoin accumulated over time.

The framework analyzes Bitcoin network and market indicators, including on-chain activity, investor behavior, and market sentiment. It then identifies patterns that may signal whether Bitcoin appears relatively undervalued, overvalued, or fairly priced. Using these signals, AdaptiveSats creates dynamic investment strategies that automatically increase purchases during potentially attractive market conditions and reduce purchases when conditions appear less favorable. Every strategy is rigorously tested against a traditional Dollar Cost Averaging (DCA) approach. The framework keeps each strategy inside the core constraints:

- fixed accumulation budget
- fixed allocation horizon, defaulting to 365 days
- no forward-looking data
- immutable historical allocations

[Read more on our blog](https://shrutisasi.github.io/AdaptiveSats/)

## Evaluation Methodology
Strategies are evaluated using Sats per Dollar (SPD) accumulated over rolling one-year windows:

- **Baseline:** Uniform DCA (equal daily allocation)
- **Pass criteria:** Strategy must outperform DCA in >50% of rolling one-year windows (Win rate > 50%)
- **No look-ahead bias:** Strict chronological train (2010–2023) / test (2024–2025) split; all signals use only past data

## Key Concepts

| Term | Description |
|------|-------------|
| **DCA (Dollar-Cost Averaging)** | Investing a fixed amount at regular intervals regardless of price - the naive baseline |
| **Sats per Dollar (SPD)** | Satoshis (1 BTC = 100,000,000 sats) accumulated per USD invested - the primary performance metric; higher is better |
| **stacksats** | Open-source Python framework used for implementing and backtesting Bitcoin accumulation strategies |
| **Halving Cycle** | Every ~4 years, Bitcoin's block reward is halved (2012, 2016, 2020, 2024) - historically a key market cycle driver |
| **MVRV** | Market Value to Realized Value - ratio of market cap to aggregate cost basis; MVRV < 1 signals undervaluation |
| **NUPL** | Net Unrealized Profit/Loss - when NUPL < 0, most holders are at a loss (capitulation signal) |
| **SOPR** | Spent Output Profit Ratio - when SOPR < 1, coins are being sold at a loss (panic selling signal) |
| **BRK Metrics** | Bitcoin Research Kit - a dataset of 41,000+ on-chain, technical, and market metrics |


## Getting Started

### Prerequisites

-   [`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (version 26.1.0 or higher)

### Setup

Open terminal and run the following commands.

1.  Clone the repository:

    ``` bash
    git clone https://github.com/ShrutiSasi/AdaptiveSats.git
    cd AdaptiveSats
    ```

2.  Create and activate the environment:

    ``` bash
    conda env create -f environment.yml 
    conda activate adaptivesats
    ```

3.  Install TinyTeX for PDF rendering:

    ``` bash
    quarto install tinytex
    ```

4. Launch JupyterLab to explore notebooks interactively:

    ``` bash
    jupyter lab
    ```

#### Rendering reports

5.  Run the jupyter notebooks either through JupyterLab interactively or using terminal commands below to generate plots and tables <br>**Note:** This step takes time as it downloads \~1GB data from google drive and splits to train & test data as the first step.

    ``` bash
    cd notebooks
    jupyter nbconvert --to notebook --execute --inplace download.ipynb
    jupyter nbconvert --to notebook --execute --inplace family_classification.ipynb
    jupyter nbconvert --to notebook --execute --inplace preliminary_eda_charts.ipynb
    jupyter nbconvert --to notebook --execute --inplace dendogram.ipynb
    ```

    **Alternatively**, open commands.txt. Check the change directory command and jupyter commands to run. Use "#" in front of a command to comment it and exclude from running. Run the below command with `AdaptiveSats` as the current/active directory in terminal (Git Bash).

    For window user:
    
    ```bash
    ./commands.txt
    ```

    For macos user:

    ```bash
    bash ./commands.txt
    ```


#### Generate proposal pdf

6.  Ensure `AdaptiveSats` is the current/active directory in terminal. Render the proposal:

    ``` bash
    cd .. #If still in notebooks folder
    quarto render docs/Proposal.qmd --to pdf
    ```

    The proposal pdf gets created at `AdaptiveSats\docs`

#### Generate final report pdf

7.  Ensure `AdaptiveSats` is the current/active directory in terminal. Render the final report:

    ``` bash
    cd .. #If still in notebooks folder
    quarto render docs/final_report.qmd --to pdf
    ```

    The final_report pdf gets created at `AdaptiveSats\docs`

## Notebook Guide

Start with core pipeline notebooks, then explore strategy notebooks

### Core Pipeline

|#|**Notebook**|**Purpose**| 
|---|---|---|
|1.|`download.ipynb`|Downloads ~1GB raw BRK metrics from Google Drive, creates `train.parquet` and `test.parquet`|
|2.|`family_classification.ipynb`|Categorizes 41,407 metrics into 16 feature families (e.g., Market Valuation, Profitability & SOPR)|
|3.|`preliminary_eda_charts.ipynb`|EDA visualizations: feature counts, family distributions, Bitcoin historical price trend and halving cycles|
|4.|`dendogram.ipynb`|Hierarchical clustering and correlation dendrograms to identify multicollinearity per family|
|-|`eda.ipynb`|Comprehensive exploratory data analysis|
|-|`btc_stl_analysis.ipynb`|STL decomposition of BTC price and on-chain metrics (trend / seasonality / residuals)|

### Strategy Notebooks

**Proposed Strategies** [proposed_strategies](notebooks/proposed_strategies)

|**Notebook**|**Strategy**|**Video Walkthrough**|
|---|---|---|
|`bayes_hmm.ipynb`|Hidden Markov Model with Bayesian inference for regime-aware allocation|[Watch Video](https://youtu.be/znfH24iVRaM)|
|`hmm-garch.ipynb`|HMM combined with GARCH volatility modelling|[Watch Video](https://youtu.be/znfH24iVRaM)|
|`composite_signal_index_strategy.ipynb`|Combines MVRV, NUPL, and SOPR into a single composite score for allocation|[Watch Video](https://youtu.be/exyRqs2gwck)|
|`external_tunable_strat.ipynb`|Integration of external macro/sentiment features|[Watch Video](https://youtu.be/krKk9pX62gQ)|
|`multi_strategy_regimes_approach.ipynb`|Multi-strategy regime-based approach that selects the best strategy by market regime and uses saved intermediate outputs for reproducible reruns|[Watch Video](https://youtu.be/FSLVe98qfoU)|

### Note on multi-strategy intermediate outputs

The notebook `notebooks/proposed_strategies/multi_strategy_regimes_approach.ipynb` uses saved intermediate outputs by default so users can run the notebook without rerunning the full grid search.

The intermediate outputs are stored in:

```text
notebooks/proposed_strategies/intermediate_outputs/multi_strategy_regimes/
```

## Data
Raw data comes from the Bitcoin Research Kit (BRK) - a comprehensive on-chain and market dataset covering Bitcoin's full history (~2009–2026):

|**File**|**Description**|**Size**|
|---|---|---|
|`brk_metrics.parquet`|236M rows × 6,274 days of on-chain metrics|~1 GB|
|`train.parquet`|Preprocessed features, 2010–2023|-|
|`test.parquet`|Preprocessed features, 2024–2025|-|
|`bitcoin_metrics_full_classification_final.csv`|Labelled metrics with family assignments|-|

## Project Structure

```
AdaptiveSats/
├── blog/                                             # Quarto blog source code and assets
│   ├── figures/                                      # Shared programmatically generated figures
│   │   ├── bear_bitcoin_cycle.png
│   │   ├── external_tunable_approach_plot.png
│   │   ├── fig_composite_signal_index_strategy.png
│   │   ├── fig_learned_signal_weights.png
│   │   ├── full_bayes_hmm_plot.png
│   │   ├── full_garch_hmm_plot.png
│   │   └── multi-strategy-approach-plot.png
│   ├── images/                                       # Static images for the blog
│   │   └── Bitcoin_logo.png
│   ├── posts/                                        # Individual strategy blog posts
│   │   ├── composite-signal-index-strategy/
│   │   │   └── index.qmd
│   │   ├── external-tunable-post/
│   │   │   └── index.qmd
│   │   ├── garch_content/
│   │   │   └── index.qmd
│   │   └── multi-strategy-regime-based-approach/
│   │       └── index.qmd
│   ├── about.qmd                                     # About page for the project team
│   ├── index.qmd                                     # Main blog landing page
│   ├── references.bib                                # Bibliography citations for the blog
│   └── styles.css                                    # Custom CSS styling for the blog
├── data/                                             # Processed and reference data files
│   ├── raw/
│   │   └── brk_metrics.parquet                       # Raw on-chain metrics (download.ipynb)
|   ├── processed/  
|   │   └── train.parquet                             # training set - 2010-2023 (created by download.ipynb)
|   │   └── test.parquet                              # test set - 2024-2025 (created by download.ipynb)
│   ├── all_col_names.csv                             # Full list of feature column names
│   ├── bitcoin_metrics_full_classification_final.csv # Labelled metrics dataset
│   ├── columns_to_drop.csv                           # Columns excluded from modelling
│   └── common_zero_var_cols.csv                      # Zero-variance columns identified in EDA
├── docs/                                             # Project documentation and reports
│   ├── figures/                                      # Generated plots and charts
│   │   ├── feature_count_by_family.png
│   │   ├── features_per_year.png
│   │   ├── fig_cycle_violin_plots.png
│   │   ├── fig_price_history.png
│   │   └── price_dendrogram_new.png
│   ├── final_report.qmd                              # Quarto source for the final report
│   ├── final_report.pdf                              # Rendered PDF final report
│   ├── Proposal.qmd                                  # Quarto source for the project proposal
│   ├── Proposal.html                                 # Rendered HTML proposal
│   ├── Proposal.pdf                                  # Rendered PDF proposal                            
│   └── references.bib                                # Bibliography
├── notebooks/                                        # Jupyter notebooks for analysis
│   ├── proposed_strategies/                          # Newly built strategies
|   │   └── bayes_hmm.ipynb                           # HMM Bayesian strategy prototype
│   │   └── hmm-garch.ipynb                           # HMM GARCH strategy prototype
|   │   └── composite_signal_index_strategy.ipynb     # Composite signal index strategy prototype
|   │   └── external_tunable_strat.ipynb              # Macro-Economic Integration with 10-Year US Treasury Yield    
│   │   └── multi_strategy_regimes_approach.ipynb     # Allocation strategy based on market regime
│   ├── research_strategies/                          # Research work
│   │   ├── bayes_hmm_look_forward.ipynb
│   │   ├── brk_include_strat.ipynb
│   │   ├── regime_strategy_analysis_initial_exploration.ipynb
│   │   └── value_floor_strat.ipynb
│   │   └── weighted_external_tunable_strat.ipynb
│   ├── stacksats_strategies/                         # Built-in stacksats strategies (Experiment based on Stacksats original models)
│   │   ├── momentum_vs_dca_4_cycles_top10_yby_halving.ipynb
│   │   ├── momentum_vs_dca_all_years_top10.ipynb
│   │   ├── experimental_strategies.ipynb
│   │   └── mvrv.ipynb
│   │   └── simple_zscore_analysis.ipynb
│   ├── btc_stl_analysis.ipynb                        # BTC price STL decomposition - Analysis
│   ├── dendogram.ipynb                               # 4. Metric correlation dendrogram
│   ├── download.ipynb                                # 1. Downloads raw data from Google Drive
│   ├── eda.ipynb                                     # Exploratory data analysis
│   ├── family_classification.ipynb                   # 2. Metric family classification
│   ├── loading_brk_metrics_data.ipynb                # Data loading and parsing to individual years - used during initial analysis
│   └── preliminary_eda_charts.ipynb                  # 3. Preliminary EDA visualisations
├── src/                                              # Source package
│   ├── __init__.py
│   └── analysis.py                                   # Group metric families and find correlation
│   └── config.py                                     # Global variables
│   └── data_utils.py                                 # Data load utilities
│   └── plots.py                                      # Shared plotting utilities
│   └── strategy_utils.py                             # Shared strategy utilities
├── environment.yml                                   # Conda environment specification
├── LICENSE
└── README.md
```

## Authors
|**Name**|**GitHub**|
|---|---|
|Arafat B. Bello|[@bbarafat](https://github.com/bbarafat)|
|Nguyen Nguyen|[@nguyen6uyen](https://github.com/nguyen6uyen)|
|Raghav Gupta|[@raghav9048](https://github.com/raghav9048)|
|Shruti Sasi|[@ShrutiSasi](https://github.com/ShrutiSasi)|

## License
This project is licensed under the MIT License. Check the [LICENSE](LICENSE) file.
