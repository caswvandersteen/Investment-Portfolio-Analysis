# Investment Portfolio Analysis

Personal project: a Python pipeline that loads my long-term equity portfolio
(55 positions in six sub-portfolios, split over two 50/50 blocks) from an Excel
workbook, validates it, and analyses exposure, performance and risk.

## Status

- [x] Load holdings from six sheets into one clean table
- [x] Validation against the workbook's control sheet (weights, target weights,
      position counts, duplicates, currency split)
- [x] Exposure by block, pie, asset type, country, and listing vs economic
      currency, reconciled with the workbook's exposure matrix
- [ ] Market data (yfinance), backtest and benchmark comparison
- [ ] Risk: correlation, VaR/ES, risk contribution, stress tests
- [ ] Power BI dashboard

## Setup (Windows)

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Data

The source workbook is not part of this repository (see `.gitignore`).
The notebooks expect it at `data/raw/portfolio_20261031.xlsx`.

## Structure

- `data/raw/` – source workbook (not tracked)
- `notebooks/` – analysis notebooks
- `src/` – reusable functions (in progress)
- `output/` – generated tables and figures (not tracked)
