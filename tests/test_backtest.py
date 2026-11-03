import numpy as np
import pandas as pd
import pytest

from portfolio_analysis.backtest import backtest, month_ends, rebalance_weights, universe_changes


@pytest.fixture
def setup():
    target = pd.Series({"a1": 0.3, "a2": 0.2, "b1": 0.5})
    groups = pd.Series({"a1": "A", "a2": "A", "b1": "B"})
    return target, groups


def test_missing_weight_is_redistributed_within_its_group(setup):
    target, groups = setup
    w = rebalance_weights(target, groups, ["a1", "b1"])
    assert w["a1"] == pytest.approx(0.5)  # gets the weight of a2
    assert w["b1"] == pytest.approx(0.5)  # other group untouched
    assert w.sum() == pytest.approx(1.0)


def test_group_without_data_gets_no_weight(setup):
    target, groups = setup
    w = rebalance_weights(target, groups, ["b1"])
    assert list(w.index) == ["b1"]


def test_constant_returns_give_constant_portfolio_return(setup):
    target, groups = setup
    dates = pd.bdate_range("2024-01-01", periods=10)
    returns = pd.DataFrame(0.01, index=dates, columns=target.index)
    port = backtest(returns, target, groups, rebalance_dates=[])
    assert np.isnan(port.iloc[0])  # no weights known before the first close
    assert port.iloc[1:].to_numpy() == pytest.approx(0.01)


def test_weights_apply_from_the_next_day(setup):
    target, groups = setup
    dates = pd.bdate_range("2024-01-01", periods=3)
    returns = pd.DataFrame({"a1": [0.0, 0.0, 0.0], "a2": [0.0, 0.0, 0.0], "b1": [0.0, 0.5, 0.0]}, index=dates)
    port = backtest(returns, target, groups, rebalance_dates=[])
    assert port.iloc[1] == pytest.approx(0.5 * 0.5)  # weight of b1 set at the close of day 0


def test_late_starter_enters_on_universe_change(setup):
    target, groups = setup
    dates = pd.bdate_range("2024-01-01", periods=4)
    returns = pd.DataFrame({"a1": 0.0, "a2": [np.nan, np.nan, 0.1, 0.1], "b1": 0.0}, index=dates)
    changes = universe_changes(returns)
    assert dates[2] in changes
    port = backtest(returns, target, groups, rebalance_dates=changes)
    assert port.iloc[2] == pytest.approx(0.0)  # a2 has no weight on its first day
    assert port.iloc[3] == pytest.approx(0.2 * 0.1)  # from the next day at its target weight


def test_month_ends_are_last_trading_days():
    dates = pd.bdate_range("2024-01-01", "2024-03-31")
    assert [d.day for d in month_ends(dates)] == [31, 29, 29]
