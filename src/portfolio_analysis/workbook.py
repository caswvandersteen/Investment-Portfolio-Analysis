"""Reading and validating the portfolio workbook."""

from pathlib import Path

import pandas as pd

from .config import CATEGORY_COLUMNS, COLUMN_NAMES, ECON_COLUMNS, NUMERIC_COLUMNS, PIE_SHEETS, TOLERANCE


def read_table(path: Path, sheet_name: str, header_label: str) -> pd.DataFrame:
    """Read a table whose header row starts with header_label in the first column.

    The table ends at the first empty cell in its first column, or at the end
    of the sheet if there is none.
    """
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
    matches = raw.index[raw[0] == header_label]
    if len(matches) == 0:
        raise ValueError(f"Header '{header_label}' not found in sheet '{sheet_name}'")

    table = pd.read_excel(path, sheet_name=sheet_name, header=int(matches[0]))
    empty = table.index[table[table.columns[0]].isna()]
    return table.iloc[: empty[0]] if len(empty) else table


def load_holdings(path: Path, pie_sheets: list[str] = PIE_SHEETS) -> pd.DataFrame:
    """All holdings of the pie sheets in one table, with English column names."""
    frames = []
    for sheet_name in pie_sheets:
        holdings = read_table(path, sheet_name, "Ticker").rename(columns=CATEGORY_COLUMNS)
        holdings["pie_sheet"] = sheet_name
        holdings["pie"] = sheet_name.split(") ", maxsplit=1)[1]
        frames.append(holdings)

    combined = pd.concat(frames, ignore_index=True).rename(columns=COLUMN_NAMES)
    for col in NUMERIC_COLUMNS:
        combined[col] = pd.to_numeric(combined[col])
    return combined


def load_targets(path: Path) -> pd.DataFrame:
    """Target weight, block and number of positions per pie from the Portfolio sheet."""
    targets = read_table(path, "Portfolio", "Pie")
    targets = targets[targets["Pie"] != "Totaal"]
    targets = targets.rename(columns={"Pie": "pie", "Doelgewicht": "target_weight", "Blok": "block", "Posities": "n_positions"})
    targets["target_weight"] = pd.to_numeric(targets["target_weight"])
    targets["n_positions"] = pd.to_numeric(targets["n_positions"])
    return targets[["pie", "target_weight", "block", "n_positions"]].reset_index(drop=True)


def validate_holdings(holdings: pd.DataFrame, targets: pd.DataFrame, tolerance: float = TOLERANCE) -> pd.Series:
    """Named pass/fail checks of the holdings against the Portfolio sheet."""
    pie_sums = holdings.groupby("pie")["weight_in_pie"].sum()
    actual = holdings.groupby("pie")["weight_in_portfolio"].sum()
    target = targets.set_index("pie")["target_weight"]
    counts = holdings.groupby("pie")["ticker"].count()
    target_counts = targets.set_index("pie")["n_positions"]
    row_sums = holdings[ECON_COLUMNS].sum(axis=1)

    return pd.Series({
        "total weight = 1": abs(holdings["weight_in_portfolio"].sum() - 1) < tolerance,
        "pie weights sum to 1": ((pie_sums - 1).abs() < tolerance).all(),
        "pie weights match targets": ((actual - target).abs() < tolerance).all(),
        "position counts match Portfolio": ((counts - target_counts) == 0).all(),
        "no empty tickers": holdings["ticker"].notna().all(),
        "no empty ISINs": holdings["isin"].notna().all(),
        "unique tickers": not holdings["ticker"].duplicated().any(),
        "unique ISINs": not holdings["isin"].duplicated().any(),
        "currency split sums to 1 per row": ((row_sums - 1).abs() < tolerance).all(),
    })
