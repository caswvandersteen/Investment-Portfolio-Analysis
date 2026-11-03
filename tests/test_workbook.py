import pandas as pd
import pytest
from openpyxl import Workbook

from portfolio_analysis.workbook import read_table


@pytest.fixture
def workbook(tmp_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Pie"
    rows = [["Title"], [None], ["Ticker", "Weight"], ["AAA", 0.6], ["BBB", 0.4], [None, None], ["Totaal", 1.0]]
    for row in rows:
        ws.append(row)
    path = tmp_path / "test.xlsx"
    wb.save(path)
    return path


def test_header_is_found_and_table_ends_at_first_empty_cell(workbook):
    table = read_table(workbook, "Pie", "Ticker")
    assert list(table["Ticker"]) == ["AAA", "BBB"]  # the Totaal row below the gap is excluded


def test_missing_header_gives_a_clear_error(workbook):
    with pytest.raises(ValueError, match="not found"):
        read_table(workbook, "Pie", "ISIN")
