# Live measurement rules

Version 1.0 · fixed on 27 November 2026, before the first measurement date
(30 November 2026).

These rules are fixed **before** any live result is known, so that the method
cannot be chosen afterwards to make the results look better. The commit date of
this file on GitHub is the record of that. Changes are only allowed under the
rules in section 8.

## 1. Scope

- **Inception of the live record:** 31 October 2026. Everything before that date
  is a backtest of the current selection and is reported separately (see
  section 7).
- **Frequency:** monthly, on every calendar month-end (the *measurement date*).
- **Currency:** all results in EUR.

## 2. Data and valuation

- **Positions and cash flows** come from the broker export (transactions:
  buys, sells, deposits, withdrawals, dividends, fees and taxes).
- **Prices:** closing price in the listing currency on the last trading day on
  or before the valuation date (Yahoo Finance, with the same jump and spike
  checks as notebook `02`).
- **Exchange rates:** ECB reference rate of the last ECB business day on or
  before the valuation date. The difference in timing with US closing prices is
  a known source of noise.
- **Valuation:** reconstructed positions × closing price × ECB rate, on every
  trading day.
- **Reconciliation:** on every measurement date the reconstructed portfolio
  value is compared with the value the broker reports. A difference above
  **0.5%** is investigated before results are reported, and the cause is
  logged.

## 3. Return measures

- **Primary measure: time-weighted return (TWR).** Daily returns between
  cash flows, chain-linked:
  `R = (1 + r1)(1 + r2)…(1 + rn) − 1`, where on a day with an external cash
  flow `r = (V_end − CF) / V_start − 1` and the cash flow is assumed to arrive
  at the end of the day. TWR measures the investment decisions and is not
  affected by the size or timing of deposits. It is the only measure compared
  with benchmarks.
- **Secondary measure: money-weighted return (MWR).** The internal rate of
  return on the actual external cash flows and the end value. It measures the
  personal result, including the timing of deposits, and is never compared with
  a benchmark.
- **Net of costs:** returns are measured after broker fees, currency conversion
  costs and withholding taxes, as they actually occurred.
- **External cash flows** are deposits and withdrawals only. Dividends, fees
  and taxes stay inside the portfolio.

## 4. Comparisons on every measurement date

1. **Portfolio versus benchmarks:** the main benchmark (50% IWDA, 35% CMOD,
   15% EIMI, rebalanced monthly) and the look-through benchmark per pie, as
   defined in notebook `04`.
2. **Portfolio versus model portfolio:** the target weights, rebalanced to
   target at every month-end close, without costs. The difference measures
   implementation: deviation from target weights, timing of deposits and costs.
3. **Weight deviation per pie** against the target weight and the bands of the
   DCA rules in the workbook.

Known asymmetry: benchmark and model returns are total returns before
withholding tax (Yahoo adjusted close), while the portfolio is measured after
tax and costs. This works slightly against the portfolio and is not corrected.

## 5. Reporting

- Every month is reported, whatever the outcome.
- Returns are reported for the month, year-to-date and since inception.
- **No annualised returns until the live record covers at least 12 months.**
  An annualised figure over a shorter period suggests a precision that does not
  exist.
- Risk measures (volatility, drawdown) are reported from the live data only once
  at least 6 months are available, and always with the number of observations.

## 6. Data and privacy

- Broker exports and anything showing amounts (values, deposits, quantities)
  stay in `data/raw/` and `output/` and are never committed.
- Only returns, weights and the price list are published.

## 7. Backtest and live record

- The backtest (from 2019) and the live record (from 31 October 2026) are never
  chained into one series. Charts and tables show them separately, with the
  inception date marked.
- Backtest results describe how the current selection *would have behaved*;
  only the live record says something about how the portfolio *is managed*.

## 8. Changes and corrections

- **Data errors** may be corrected afterwards. Every correction is logged in
  `data/reference/live_corrections.csv` with date, measurement date, what
  changed and why, and is only made after checking a third source.
- **Method changes** apply only to measurement dates after the change, never
  to earlier ones. They raise the version number of this file and are
  described below.
- Changes to holdings or target weights are logged in the decision log of the
  workbook. Benchmarks are not changed because of results.

## Change log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-27 | First version, before the first measurement date |
