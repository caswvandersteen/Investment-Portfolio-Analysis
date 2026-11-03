import pandas as pd
import pytest

from portfolio_analysis.performance import metrics, to_weekly


def test_weekly_returns_compound_daily_returns():
    dates = pd.bdate_range("2024-01-01", periods=5)  # Monday to Friday
    weekly = to_weekly(pd.Series(0.01, index=dates))
    assert weekly.iloc[0] == pytest.approx(1.01 ** 5 - 1)


def test_max_drawdown():
    dates = pd.bdate_range("2024-01-01", periods=3)
    r = pd.Series([0.10, -0.50, 0.20], index=dates)
    stats = metrics(r, pd.Series(0.0, index=dates))
    assert stats["max_drawdown"] == pytest.approx(-0.50)
