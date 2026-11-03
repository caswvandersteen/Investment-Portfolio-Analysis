import numpy as np
import pandas as pd
import pytest

from portfolio_analysis.market_data import apply_overrides, ticker_returns, to_eur


def test_pence_are_converted_and_divided_by_fx():
    dates = pd.bdate_range("2024-01-01", periods=2)
    prices = pd.DataFrame({"X.L": [1000.0, 1100.0]}, index=dates)
    fx = pd.DataFrame({"GBP": [0.8, 0.8]}, index=dates)
    eur = to_eur(prices, pd.Series({"X.L": "GBp"}), fx)
    assert eur["X.L"].iloc[0] == pytest.approx(12.5)  # 1000 pence = 10 GBP = 12.5 EUR


def test_no_backward_fill_before_a_series_starts():
    dates = pd.bdate_range("2024-01-01", periods=3)
    prices = pd.DataFrame({"E": [np.nan, 10.0, 11.0]}, index=dates)
    eur = to_eur(prices, pd.Series({"E": "EUR"}), pd.DataFrame(index=dates))
    assert np.isnan(eur["E"].iloc[0])


def test_overrides_drop_the_listed_dates():
    dates = pd.bdate_range("2024-01-01", periods=3)
    prices = pd.DataFrame({"S": [1.0, 99.0, 1.0]}, index=dates)
    overrides = pd.DataFrame({"yahoo_symbol": ["S"], "start_date": [dates[1]], "end_date": [dates[1]]})
    assert np.isnan(apply_overrides(prices, overrides)["S"].iloc[1])


def test_proxy_is_used_only_before_the_actual_series_starts():
    dates = pd.bdate_range("2024-01-01", periods=5)
    prices = pd.DataFrame({
        "ACT": [np.nan, np.nan, 10.0, 11.0, 12.0],
        "PRX": [100.0, 110.0, 121.0, 100.0, 100.0],
    }, index=dates)
    series = pd.DataFrame({"ticker": ["T", "T"], "yahoo_symbol": ["ACT", "PRX"], "series": ["actual", "proxy"]})
    returns, source = ticker_returns(prices, series)
    assert returns["T"].iloc[1] == pytest.approx(0.10)  # proxy before the start
    assert returns["T"].iloc[3] == pytest.approx(0.10)  # actual afterwards, not the proxy's -17%
    assert source["T"].iloc[1] == "proxy" and source["T"].iloc[3] == "actual"
