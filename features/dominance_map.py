import pandas as pd
import plotly.express as px
import streamlit as st

from utils.filters import first_innings, exclude_no_result

# Limit heatmap axes to keep it readable
TOP_VENUES = 20
TOP_TEAMS = 12


def dominance_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Win counts per (venue, winning team), one row per match."""
    base = exclude_no_result(first_innings(df))
    return (
        base.groupby(["venue", "winner"])
        .agg(wins=("match_id", "nunique"))
        .reset_index()
    )


def render_dominance_map(df: pd.DataFrame) -> None:
    stats = dominance_stats(df)

    if stats.empty:
        st.warning("No data for the selected filters.")
        return

    # Pick the most-played venues and most-winning teams to cap axis size
    top_venues = (
        stats.groupby("venue")["wins"].sum()
        .nlargest(TOP_VENUES)
        .index.tolist()
    )
    top_teams = (
        stats.groupby("winner")["wins"].sum()
        .nlargest(TOP_TEAMS)
        .index.tolist()
    )

    filtered = stats[
        stats["venue"].isin(top_venues) & stats["winner"].isin(top_teams)
    ]

    # Build the pivot matrix (venues × teams); fill missing combos with 0
    pivot = (
        filtered.pivot_table(index="venue", columns="winner", values="wins", aggfunc="sum")
        .reindex(index=top_venues, columns=top_teams)
        .fillna(0)
        .astype(int)
    )

    # Sort venues by total wins (most active at top)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=True).index]

    col_opts, _ = st.columns([2, 3])
    with col_opts:
        metric = st.radio(
            "Show",
            ["Win count", "Win % at venue"],
            horizontal=True,
            key="dom_metric",
        )

    if metric == "Win % at venue":
        row_totals = pivot.sum(axis=1)
        display = pivot.div(row_totals, axis=0).mul(100).round(1)
        color_label = "Win %"
        fmt = ".1f"
    else:
        display = pivot
        color_label = "Wins"
        fmt = "d"

    fig = px.imshow(
        display,
        color_continuous_scale="YlOrRd",
        aspect="auto",
        labels={"x": "Team", "y": "Venue", "color": color_label},
        title=f"Team Dominance by Venue — {color_label} (top {TOP_VENUES} venues · top {TOP_TEAMS} teams)",
        text_auto=fmt,
    )
    fig.update_layout(
        height=600,
        xaxis_tickangle=-45,
        coloraxis_colorbar_title=color_label,
        margin=dict(l=250),
    )
    fig.update_traces(textfont_size=10)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw win counts"):
        st.dataframe(
            pivot.rename_axis("Venue").rename_axis("Team", axis=1),
            use_container_width=True,
        )
