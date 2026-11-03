"""Return aggregation and performance statistics."""

import numpy as np
import pandas as pd

from .config import TRADING_DAYS


def to_weekly(daily):
    """Compound daily returns into Friday-to-Friday weekly returns."""
    return (1 + daily).resample("W-FRI").prod(min_count=1) - 1


def metrics(r: pd.Series, rf: pd.Series, bench: pd.Series | None = None, periods: int = TRADING_DAYS) -> dict:
    """Annualised return, volatility, Sharpe, Sortino, max drawdown and, with a benchmark, beta, TE and IR."""
    r = r.dropna()
    rf = rf.reindex(r.index).fillna(0.0)
    excess = r - rf
    ann = np.sqrt(periods)
    wealth = (1 + r).cumprod()
    downside = np.sqrt((excess.clip(upper=0) ** 2).mean()) * ann
    out = {
        "start": r.index.min().date(),
        "ann_return": wealth.iloc[-1] ** (periods / len(r)) - 1,
        "ann_vol": r.std() * ann,
        "sharpe": excess.mean() * periods / (r.std() * ann),
        "sortino": excess.mean() * periods / downside,
        "max_drawdown": (wealth / wealth.cummax() - 1).min(),
    }
    if bench is not None:
        both = pd.concat([r, bench.reindex(r.index)], axis=1, sort=True).dropna()
        active = both.iloc[:, 0] - both.iloc[:, 1]
        tracking_error = active.std() * ann
        out["beta"] = both.cov().iloc[0, 1] / both.iloc[:, 1].var()
        out["tracking_error"] = tracking_error
        out["information_ratio"] = active.mean() * periods / tracking_error
    return out
