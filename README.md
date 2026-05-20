# AdaptiveSats
Python Library for quantitative long only Bitcoin accumulation - keeping the discipline of Dollar-Cost Averaging but also takes into account the market volatility, on-chain, macro and sentiment data to improve purchase timing.

1. Create and activate the environment:
```bash
   conda env create -f environment.yml
   conda activate adaptivesats
```

2. Install TinyTeX for PDF rendering
```bash
    quarto install tinytex
```

3. Render the proposal:
```bash
    quarto render docs/Proposal.qmd
```