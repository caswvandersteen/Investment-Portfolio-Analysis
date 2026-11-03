"""Fixed settings shared by the notebooks: workbook layout, column names, tolerances."""

TRADING_DAYS = 252
WEEKS = 52
TOLERANCE = 1e-9

PIE_SHEETS = [
    "1) Kwaliteit",
    "2) Thematisch",
    "3) AI Boom",
    "4) Energie",
    "5) Mijnbouw",
    "6) Multipolaire Wereldorde",
]

BLOCKS = {
    "A": ["Kwaliteit", "Thematisch", "AI Boom"],
    "B": ["Energie", "Mijnbouw", "Multipolaire Wereldorde"],
}

CATEGORY_COLUMNS = {"Thema": "category", "Ketenlaag": "category", "Regio": "category"}

COLUMN_NAMES = {
    "Ticker": "ticker",
    "Naam": "name",
    "ISIN": "isin",
    "Type": "asset_type",
    "Model": "model",
    "Weging pie": "weight_in_pie",
    "Weging portf.": "weight_in_portfolio",
    "Land": "country",
    "Beurs": "exchange",
    "Not. valuta": "listing_currency",
    "TER": "ter",
    "Replicatie": "replication",
    "Uitkering": "distribution",
    "USD": "econ_usd",
    "EUR": "econ_eur",
    "GBP": "econ_gbp",
    "CHF": "econ_chf",
    "CAD": "econ_cad",
    "Overig ontw.": "econ_other_dm",
    "Opkomend": "econ_em",
    "Controle valuta": "econ_check",
    "Hoofdvaluta": "main_currency",
    "Div. rendement": "dividend_yield",
    "Cijfer": "score",
    "Rating": "rating",
    "Rol: waarom deze positie": "role",
}

ECON_COLUMNS = ["econ_usd", "econ_eur", "econ_gbp", "econ_chf", "econ_cad", "econ_other_dm", "econ_em"]

NUMERIC_COLUMNS = ["weight_in_pie", "weight_in_portfolio", "ter", *ECON_COLUMNS, "dividend_yield", "score"]
