"""Backtest of fixed target weights with drift between rebalance dates."""

import numpy as np
import pandas as pd


def rebalance_weights(target: pd.Series, groups: pd.Series, available) -> pd.Series:
    """Target weights with each group's weight redistributed over its available members.

    A group without any available member gets no weight.
    """
    w = target[list(available)]
    if w.empty:
        return w
    group_target = target.groupby(groups).sum()
    group_available = w.groupby(groups[w.index]).sum()
    scale = (group_target / group_available).reindex(groups[w.index].values).values
    return w * scale


def backtest(returns: pd.DataFrame, target: pd.Series, groups: pd.Series, rebalance_dates) -> pd.Series:
    """Daily portfolio returns; weights drift with returns between rebalance dates.

    Weights set at the close of day t apply to the returns of day t+1, so no
    return is used before it is known.
    """
    returns = returns[target.index]
    started = returns.notna().cummax()
    rebalance_dates = set(rebalance_dates)
    out = pd.Series(np.nan, index=returns.index)
    w = None
    for date, row in returns.iterrows():
        if w is not None and w.sum() > 0:
            r = row[w.index].fillna(0.0)
            out[date] = (w * r).sum() / w.sum()
            w = w * (1 + r)
        if w is None or w.sum() == 0 or date in rebalance_dates:
            available = started.loc[date][started.loc[date]].index
            w = rebalance_weights(target, groups, available)
    return out


def month_ends(index: pd.DatetimeIndex) -> list:
    """Last trading day of each month."""
    return index.to_series().groupby(index.to_period("M")).max().tolist()


def universe_changes(returns: pd.DataFrame) -> list:
    """Dates on which at least one column gets its first return."""
    started = returns.notna().cummax()
    changed = started.astype(int).diff().fillna(0).gt(0).any(axis=1)
    return returns.index[changed].tolist()
