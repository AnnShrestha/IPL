import pandas as pd


def regulation_innings(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only innings 1 and 2 — drops super-over rows (innings 3–6)."""
    return df[df["innings"].isin([1, 2])]


def first_innings(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only innings 1 rows. Used for per-match aggregations to avoid
    double-counting a match's venue/toss metadata."""
    return df[df["innings"] == 1]


def exclude_no_result(df: pd.DataFrame) -> pd.DataFrame:
    """Drop matches with no result (winner column is an empty string).
    Must be applied before any win-rate calculation."""
    return df[df["winner"] != ""]
