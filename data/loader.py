import pandas as pd
import streamlit as st

from utils.venue_aliases import VENUE_ALIASES, TEAM_ALIASES

CSV_PATH = "ipl_2008_2024_complete.csv"

NEUTRAL_SEASONS = {2009, 2014, 2020, 2021}


@st.cache_data
def load_data(
    exclude_dl: bool = True,
    exclude_neutral: bool = False,
    regulation_only: bool = True,
) -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)

    # Normalize venue and team names before any grouping
    df["venue"] = df["venue"].replace(VENUE_ALIASES)
    df["batting_team"] = df["batting_team"].replace(TEAM_ALIASES)
    df["bowling_team"] = df["bowling_team"].replace(TEAM_ALIASES)

    # season is stored as float (2008.0) in the CSV
    df["season"] = df["season"].astype(int)

    # Drop super-over rows (innings 3–6)
    if regulation_only:
        df = df[df["innings"].isin([1, 2])]

    # Drop DLS-affected matches — phase stats are unreliable for these
    if exclude_dl:
        df = df[df["method"] != "D/L"]

    # Optionally drop matches played at neutral (non-Indian) venues
    if exclude_neutral:
        df = df[~df["season"].isin(NEUTRAL_SEASONS)]

    return df.reset_index(drop=True)


if __name__ == "__main__":
    df = load_data(exclude_dl=True, regulation_only=True)

    assert df["venue"].nunique() <= 39, (
        f"Venue normalization incomplete: {df['venue'].nunique()} unique venues"
    )
    assert set(df["innings"].unique()).issubset({1, 2}), (
        f"Super-over rows leaked in: innings values {df['innings'].unique()}"
    )
    assert (df["method"] == "D/L").sum() == 0, "DLS rows present after filtering"
    assert 2000 <= len(df) <= 2200, f"Unexpected row count: {len(df)}"
    assert df["season"].dtype in ("int32", "int64"), (
        f"season dtype is {df['season'].dtype}, expected int"
    )
    assert set(df["toss_win_match_win"].dropna().unique()).issubset({0.0, 1.0}), (
        "Unexpected toss_win_match_win values"
    )

    pp_rate = df[df["innings"] == 1]["powerplay_runs"] / 6
    assert pp_rate.between(2, 25).all(), "Outlier powerplay rates detected"

    print(f"Rows: {len(df)} | Matches: {df['match_id'].nunique()} | Venues: {df['venue'].nunique()}")
    print("All data assertions passed.")
