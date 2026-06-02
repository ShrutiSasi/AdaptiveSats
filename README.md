# AdaptiveSats

Python Library for quantitative long only Bitcoin accumulation - keeping the discipline of Dollar-Cost Averaging but also takes into account the market volatility, on-chain, macro and sentiment data to improve purchase timing.


## Project Structure

```
AdaptiveSats/
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
│   ├── Proposal.qmd                                  # Quarto source for the project proposal
│   ├── Proposal.html                                 # Rendered HTML proposal
│   ├── Proposal.pdf                                  # Rendered PDF proposal
│   └── references.bib                                # Bibliography
├── notebooks/                                        # Jupyter notebooks for analysis
│   ├── proposed_strategies/                          # Newly built strategies
│   │   └── composite_signal_index_strategy.ipynb     # Composite signal index strategy prototype
│   │   └── hmm-garch.ipynb                           # HMM GARCH strategy prototype
|   │   └── bayes_hmm.ipynb                           # HMM Bayesian strategy prototype
|   │   └── regime_strategy_analysis.ipynb            # Allocation strategy based on market regime
│   ├── stacksats_strategies/                         # Built-in stacksats strategies
│   │   ├── momentum_vs_dca_4_cycles_top10_yby_halving.ipynb
│   │   ├── momentum_vs_dca_all_years_top10.ipynb
│   │   ├── experimental_strategies.ipynb
│   │   └── simple_zscore_analysis.ipynb
│   ├── btc_stl_analysis.ipynb                        # BTC price STL decomposition - Analysis
│   ├── dendogram.ipynb                               # 4. Metric correlation dendrogram
│   ├── download.ipynb                                # 1. Downloads raw data from Google Drive
│   ├── eda.ipynb                                     # Exploratory data analysis
│   ├── family_classification.ipynb                   # 2. Metric family classification
│   ├── loading_brk_metrics_data.ipynb                # Data loading and parsing to individual years - not used
│   └── preliminary_eda_charts.ipynb                  # 3. Preliminary EDA visualisations
├── src/                                              # Source package
│   ├── __init__.py
│   └── analysis.py                                  
│   └── config.py                                     # Global variables
│   └── data_utils.py                                 # Data load utilities
│   └── plots.py                                      # Shared plotting utilities
│   └── strategy_utils.py                            
├── environment.yml                                   # Conda environment specification
├── LICENSE
└── README.md
```

## Setup

### Prerequisites

-   [`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (version 26.1.0 or higher)

### Instructions

1.  Open terminal and run the following commands.

2.  Clone the repository:

``` bash
git clone https://github.com/ShrutiSasi/AdaptiveSats.git
cd AdaptiveSats
```

3.  Create and activate the environment:

``` bash
 conda env create -f environment.yml 
 conda activate adaptivesats
```

4.  Install TinyTeX for PDF rendering:

``` bash
quarto install tinytex
```

#### Rendering reports (Optional)

5.  Run the jupyter notebooks to generate plots and tables (**optional** - since the plots have already been generated) <br>**Note:** This step takes time as it downloads \~1GB data from google drive and splits to train & test data as the first step.

``` bash
cd notebooks
jupyter nbconvert --to notebook --execute --inplace download.ipynb
jupyter nbconvert --to notebook --execute --inplace family_classification.ipynb
jupyter nbconvert --to notebook --execute --inplace preliminary_eda_charts.ipynb
jupyter nbconvert --to notebook --execute --inplace dendogram.ipynb
```

#### Generate proposal pdf

6.  Ensure `AdaptiveSats` is the current/active directory in terminal. Render the proposal:

``` bash
cd .. #If still in notebooks folder
quarto render docs/Proposal.qmd
```

The proposal pdf gets created at `AdaptiveSats\docs`
