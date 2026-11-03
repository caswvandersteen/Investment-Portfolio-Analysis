"""Regression, VaR/ES, VaR backtesting, risk contribution and scenarios."""

from statistics import NormalDist

import numpy as np
import pandas as pd

Z = NormalDist()


def ols(y: pd.Series, X: pd.DataFrame) -> pd.DataFrame:
    """OLS with intercept: coefficients, standard errors and t-stats; R2 and n in attrs."""
    data = pd.concat([y, X], axis=1, sort=True).dropna()
    yv = data.iloc[:, 0].to_numpy()
    Xv = np.column_stack([np.ones(len(data)), data.iloc[:, 1:].to_numpy()])
    coef, *_ = np.linalg.lstsq(Xv, yv, rcond=None)
    resid = yv - Xv @ coef
    dof = len(yv) - Xv.shape[1]
    se = np.sqrt(np.diag(resid @ resid / dof * np.linalg.inv(Xv.T @ Xv)))
    out = pd.DataFrame({"coef": coef, "se": se, "t": coef / se}, index=["const", *X.columns])
    out.attrs["r2"] = 1 - resid.var() / yv.var()
    out.attrs["n"] = len(yv)
    return out


def historical_var_es(r: pd.Series, level: float) -> tuple[float, float]:
    """Historical VaR and ES as positive loss numbers."""
    cutoff = r.quantile(1 - level)
    return -cutoff, -r[r <= cutoff].mean()


def normal_var_es(mu: float, sigma: float, level: float) -> tuple[float, float]:
    """Parametric VaR and ES under a normal distribution, as positive loss numbers."""
    z = Z.inv_cdf(1 - level)
    return -(mu + z * sigma), -(mu - sigma * Z.pdf(z) / (1 - level))


def simulate_portfolio(pie_returns: pd.DataFrame, weights: pd.Series, n_sims: int, horizon: int,
                       dist: str = "normal", nu: float | None = None, seed: int = 42) -> tuple[pd.Series, pd.Series]:
    """Monte Carlo 1-day and horizon-day portfolio returns from a joint normal or Student-t model."""
    rng = np.random.default_rng(seed)
    mean = pie_returns.mean().to_numpy()
    cov = pie_returns.cov().to_numpy()
    w = weights[pie_returns.columns].to_numpy()
    if dist == "normal":
        shocks = rng.multivariate_normal(np.zeros(len(mean)), cov, size=(n_sims, horizon))
    elif dist == "t":
        normal = rng.multivariate_normal(np.zeros(len(mean)), cov * (nu - 2) / nu, size=(n_sims, horizon))
        shocks = normal * np.sqrt(nu / rng.chisquare(nu, size=(n_sims, horizon, 1)))
    else:
        raise ValueError("dist must be 'normal' or 't'")
    daily = (mean + shocks) @ w
    return pd.Series(daily[:, 0]), pd.Series(np.prod(1 + daily, axis=1) - 1)


def kupiec(exceedances: int, n: int, p: float) -> float:
    """Kupiec proportion-of-failures likelihood ratio (chi-squared, 1 df; 3.84 at 5%)."""
    x = exceedances
    if x == 0:
        return -2 * n * np.log(1 - p)
    phat = x / n
    return -2 * ((n - x) * np.log(1 - p) + x * np.log(p) - (n - x) * np.log(1 - phat) - x * np.log(phat))


def ewma_volatility(r: pd.Series, lam: float = 0.94, seed_days: int = 30) -> pd.Series:
    """One-day-ahead EWMA volatility: the value on day t uses returns up to t-1."""
    values = r.to_numpy()
    var = np.empty(len(values))
    var[0] = np.var(values[:seed_days])
    for t in range(1, len(values)):
        var[t] = lam * var[t - 1] + (1 - lam) * values[t - 1] ** 2
    return pd.Series(np.sqrt(var), index=r.index)


def risk_contribution(returns: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Share of portfolio variance per column (Euler decomposition); sums to 1."""
    w = weights[returns.columns]
    cov = returns.cov()
    return w * (cov @ w) / (w @ cov @ w)


def scenario_impact(shocks: dict, betas: pd.DataFrame, weights: pd.Series) -> tuple[pd.Series, float]:
    """Linear factor impact per group and for the weighted total."""
    move = pd.Series(shocks)
    per_group = betas[move.index] @ move
    return per_group, float((per_group * weights[per_group.index]).sum())
