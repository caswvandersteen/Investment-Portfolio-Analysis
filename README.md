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
- [x] Market data: Yahoo Finance prices, ECB exchange rates, documented proxies
      and price corrections, stored in SQLite
- [x] SQL on the portfolio database, including data-quality checks
- [x] Backtest of current weights (monthly rebalanced and buy-and-hold) against
      the main and look-through benchmarks, with risk-adjusted metrics, and a
      reconciliation with the workbook's return archive
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
Prices come from Yahoo Finance (primary source, with automated jump and spike
checks and corrections documented in `data/reference/price_overrides.csv`);
the manually maintained workbook is used as an independent check.

## Structure

- `data/raw/` – source workbook (not tracked)
- `data/reference/` – Yahoo symbol mapping and documented price corrections
- `data/processed/` – derived data and SQLite database (not tracked, rebuilt by the notebooks)
- `notebooks/` – `01` holdings, validation and exposure; `02` market data;
  `03` SQL; `04` backtest and performance
- `src/` – reusable functions (in progress)
- `output/` – generated tables and figures (not tracked)