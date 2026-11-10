# Investment Portfolio Analysis

A Python, SQL and Power BI project on my own long-term equity portfolio:
55 positions in six sub-portfolios ("pies"), split over two blocks of 50%
each. Block A (Growth & Quality) and block B (Macro thesis: energy, mining,
multipolar world) are designed as complementary answers to uncertainty about
inflation, interest rates and geopolitics.

## Scope

This repository covers the equity portfolio only, which is one part of my
total balance sheet. Physical gold and silver and self-custodied bitcoin are
out of scope. Everything before 31-10-2026, the first live measurement date,
is a backtest of today's selection and contains hindsight.

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
      the main and look-through benchmarks, with a reconciliation with the
      workbook's return archive
- [x] Risk: correlation between blocks, real-rate sensitivity, VaR/ES with a
      VaR backtest, risk contribution, historical stress tests, currency risk
- [x] Scenario analysis per macro regime (factor model), Taiwan shock in two variants, real returns
- [x] Power BI data model (star schema) with measures reconciled against Python
- [x] Dashboard page 1: composition and exposure
- [ ] Dashboard page 2: performance versus benchmark
- [ ] Dashboard page 3: risk and scenarios

## Power BI dashboard

Notebook `06` exports the results as a star schema (Parquet, which keeps data
types and avoids decimal-comma issues in a Dutch Power BI installation).

- **Single source of truth.** Risk-adjusted metrics (Sharpe, Sortino, drawdown,
  tracking error) are calculated once in Python and shown as-is. DAX is used for
  measures that must respond to date filters, such as the period return
  (geometric linking of daily returns).
- **Reconciliation.** Annualised return and volatility are independently
  recalculated in DAX and match the Python results for 2019–now and for 2022.
  A hidden `Checks` page in the report holds this reconciliation.
- **Integrity checks.** Notebook `06` asserts that every series in the
  performance table exists in the series dimension, and that every country has
  an English label. The first check was added after finding two unmatched
  series keys.
- **Reading notes.** The country chart shows country of domicile or listing;
  most UCITS ETFs are domiciled in Ireland, so the economic currency exposure
  is the better view of economic risk. The top-10 table shows 11 rows because
  three positions share the same weight at rank 9.
  
## Key findings (backtest 2019-2026)

These describe how the current selection *would have behaved*; they are not
evidence of skill.

- **Diversification depends on the regime.** Weekly correlation between the
  blocks is 0.62 overall, 0.17 at its low in the 2022 rate shock (block B
  +12.6% while block A fell 24.5%) and 0.88 in the Covid crash (both blocks
  fell, block B more).
- **The real interest rate is the shared driver.** Both blocks fall
  significantly when the US 10-year real yield rises, also after controlling
  for the equity market; mining and quality pies are the most sensitive.
- **Risk is split 50/50 between the blocks**, matching the capital split;
  mining carries the largest risk share relative to its capital weight.
- **Only filtered historical simulation passes the VaR backtest.** Fixed-window
  and EWMA-normal models fail the Kupiec test (too slow, or tails too thin);
  99% one-day ES is about 40% higher historically than under a normal
  distribution.
- **Effective USD exposure is about two thirds**, well above the 44% listing
  and 49% economic USD share, because several other currencies move with the
  dollar.

## Method and limitations

- **Hindsight and selection bias**: today's positions, chosen in 2026.
- **Coverage**: about 91-93% of today's weight has data in 2020 and 2022;
  missing positions are redistributed within their pie.
- **Proxies**: four funds use a fund on the same or a near-identical index
  before their own data starts (notably EPIN until February 2026).
- **Asynchronous closes**: daily returns across exchanges understate
  co-movement, so correlations and regressions use weekly returns.
- **FX**: ECB reference rates (14:15 CET) versus later closing prices add
  noise to daily EUR returns.

## Data

The source workbook is not part of this repository (see `.gitignore`).
The notebooks expect it at `data/raw/portfolio_20261031.xlsx`.

Prices come from Yahoo Finance (primary source, with automated jump and spike
checks and corrections documented in `data/reference/price_overrides.csv`);
the manually maintained workbook is used as an independent check.
Exchange rates and €STR come from the ECB, the US real yield from FRED.

## Setup (Windows)
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest

```
Run the notebooks in order: 01 to 06

## Structure

- `data/raw/` – source workbook (not tracked)
- `data/reference/` – Yahoo symbol mapping and documented price corrections
- `data/processed/` – derived data and SQLite database (not tracked, rebuilt by the notebooks)
- `notebooks/` – `01` holdings, validation and exposure; `02` market data;
  `03` SQL; `04` backtest and performance; `05` risk; `06` Power BI export
- `src/portfolio_analysis/` – reusable functions (workbook, market data, backtest, performance, risk)
- `tests/` – unit tests of the methodology (no look-ahead, within-pie redistribution, proxy splicing, VaR)
- `output/` – generated tables and figures (not tracked)
