import numpy as np
import pandas as pd
import pytest

from portfolio_analysis.risk import ewma_volatility, historical_var_es, kupiec, normal_var_es, ols, risk_contribution, scenario_impact


def test_kupiec_is_zero_when_rate_matches_expectation():
    assert kupiec(10, 1000, 0.01) == pytest.approx(0.0, abs=1e-9)
    assert kupiec(30, 1000, 0.01) > 3.84


def test_normal_var_matches_textbook_value():
    var, es = normal_var_es(0.0, 0.01, 0.99)
    assert var == pytest.approx(0.02326, abs=1e-4)
    assert es > var


def test_historical_var_and_es_are_positive_losses():
    r = pd.Series(np.linspace(-0.10, 0.10, 201))
    var, es = historical_var_es(r, 0.95)
    assert var == pytest.approx(0.09, abs=1e-9)
    assert es > var


def test_ewma_uses_only_past_returns():
    r = pd.Series(np.random.default_rng(0).normal(0, 0.01, 100))
    shocked = r.copy()
    shocked.iloc[-1] = -0.5
    assert ewma_volatility(r).iloc[-1] == ewma_volatility(shocked).iloc[-1]


def test_risk_contributions_sum_to_one():
    returns = pd.DataFrame(np.random.default_rng(1).normal(0, 0.01, (500, 3)), columns=list("abc"))
    contribution = risk_contribution(returns, pd.Series({"a": 0.5, "b": 0.3, "c": 0.2}))
    assert contribution.sum() == pytest.approx(1.0)


def test_ols_recovers_known_coefficients():
    rng = np.random.default_rng(2)
    x = pd.DataFrame({"x": rng.normal(size=1000)})
    y = pd.Series(1.0 + 2.0 * x["x"] + rng.normal(scale=0.01, size=1000))
    model = ols(y, x)
    assert model.loc["x", "coef"] == pytest.approx(2.0, abs=0.01)
    assert model.loc["const", "coef"] == pytest.approx(1.0, abs=0.01)


def test_scenario_impact_is_weighted_sum():
    betas = pd.DataFrame({"market": [1.0, 0.5]}, index=["p1", "p2"])
    per_group, total = scenario_impact({"market": -0.2}, betas, pd.Series({"p1": 0.5, "p2": 0.5}))
    assert per_group["p2"] == pytest.approx(-0.1)
    assert total == pytest.approx(-0.15)
