"""Market data: Yahoo prices, ECB rates, data corrections, EUR conversion and proxy splicing."""

import pandas as pd


def check_symbol(symbol: str, start: str) -> dict:
    """Availability, currency and history length of one Yahoo symbol."""
    import yfinance as yf

    ticker = yf.Ticker(symbol)
    try:
        hist = ticker.history(start=start, auto_adjust=False)
    except Exception as exc:  # network or parsing errors are reported, not raised
        return {"available": False, "error": str(exc)}
    if hist.empty:
        return {"available": False, "error": "no data"}
    return {
        "available": True,
        "yahoo_currency": ticker.history_metadata.get("currency"),
        "first_date": hist.index.min().date(),
        "n_obs": len(hist),
    }


def download_prices(symbols: list[str], start: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Daily Close and Adj Close (dividend and split adjusted) for a list of Yahoo symbols."""
    import yfinance as yf

    data = yf.download(symbols, start=start, auto_adjust=False, progress=False)
    return data["Close"], data["Adj Close"]


def fetch_ecb_rates(currencies: list[str], start: str) -> pd.DataFrame:
    """Daily ECB reference rates (1 EUR = X currency) as a date x currency table."""
    url = (
        f"https://data-api.ecb.europa.eu/service/data/EXR/D.{'+'.join(currencies)}.EUR.SP00.A"
        f"?format=csvdata&startPeriod={start}"
    )
    raw = pd.read_csv(url)
    rates = raw.pivot(index="TIME_PERIOD", columns="CURRENCY", values="OBS_VALUE")
    rates.index = pd.to_datetime(rates.index)
    return rates.sort_index()


def apply_overrides(prices: pd.DataFrame, overrides: pd.DataFrame) -> pd.DataFrame:
    """Set prices to NaN for every (yahoo_symbol, start_date, end_date) row in overrides."""
    prices = prices.copy()
    for _, row in overrides.iterrows():
        mask = (prices.index >= row["start_date"]) & (prices.index <= row["end_date"])
        prices.loc[mask, row["yahoo_symbol"]] = float("nan")
    return prices


def to_eur(prices: pd.DataFrame, currency_by_symbol: pd.Series, fx: pd.DataFrame, max_fill_days: int = 5) -> pd.DataFrame:
    """Convert local prices to EUR column by column.

    Pence (GBp) become pounds; short gaps are forward-filled, never backward, so
    dates before a series starts stay NaN.
    """
    fx_aligned = fx.reindex(prices.index).ffill(limit=max_fill_days)
    eur = pd.DataFrame(index=prices.index)
    for symbol in prices.columns:
        local = prices[symbol].ffill(limit=max_fill_days)
        currency = currency_by_symbol[symbol]
        if currency == "GBp":
            local = local / 100
            currency = "GBP"
        eur[symbol] = local if currency == "EUR" else local / fx_aligned[currency]
    return eur


def ticker_returns(eur_prices: pd.DataFrame, series: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Daily EUR returns per ticker, with proxy returns only before the actual series starts.

    `series` has one row per (ticker, series) with columns ticker, yahoo_symbol
    and series ("actual" or "proxy"). Returns are spliced, not prices, so a level
    difference between two funds does not create a jump.
    """
    returns = eur_prices.pct_change(fill_method=None)
    out, source = {}, {}
    for ticker, rows in series.groupby("ticker"):
        actual = returns[rows.loc[rows["series"] == "actual", "yahoo_symbol"].iloc[0]]
        combined = actual.copy()
        used = pd.Series("actual", index=returns.index).where(actual.notna())
        proxy_rows = rows[rows["series"] == "proxy"]
        if not proxy_rows.empty:
            proxy = returns[proxy_rows["yahoo_symbol"].iloc[0]]
            before_start = returns.index < actual.first_valid_index()
            combined[before_start] = proxy[before_start]
            used[before_start & proxy.notna()] = "proxy"
        out[ticker] = combined
        source[ticker] = used
    return pd.DataFrame(out), pd.DataFrame(source)
