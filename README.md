# AdaptiveSats
Python Library for quantitative long only Bitcoin accumulation - keeping the discipline of Dollar-Cost Averaging but also takes into account the market volatility, on-chain, macro and sentiment data to improve purchase timing.

## Setup

### Prerequisites

-   [`conda`](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (version 26.1.0 or higher)

### Instructions

1.  Open terminal and run the following commands.

2.  Clone the repository:

    ```bash
    git clone https://github.com/ShrutiSasi/AdaptiveSats.git
    cd AdaptiveSats
    ```

3. Create and activate the environment:
    ```bash
    conda env create -f environment.yml
    conda activate adaptivesats
    ```

4. Install TinyTeX for PDF rendering
    ```bash
        quarto install tinytex
    ```

5. Run the jupyter notebooks to generate plots and tables (**optional** - since the plots have already been generated)
<br>**Note:** This step takes time as it downloads ~1GB data from google drive and splits to train & test data as the first step.
    ```bash
        cd notebooks
        jupyter nbconvert --to notebook --execute --inplace download.ipynb
        jupyter nbconvert --to notebook --execute --inplace preliminary_eda_charts.ipynb
        jupyter nbconvert --to notebook --execute --inplace family_classification.ipynb
        jupyter nbconvert --to notebook --execute --inplace dendogram.ipynb
    ```

6. Ensure `AdaptiveSats` folder is active in terminal. Render the proposal:
    ```bash
        quarto render docs/Proposal.qmd
    ```
    The proposal pdf gets created at `AdaptiveSats\docs`