import pandas as pd
import plotly.express as px
import streamlit as st

from utils.filters import first_innings, exclude_no_result

MIN_MATCHES = 10


def toss_strategy_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Win rate by toss decision per venue.

    Uses innings-1 rows (one row per match) and excludes no-result matches.
    Uses the pre-computed toss_win_match_win column — never recomputes it.
    """
    inn1 = exclude_no_result(first_innings(df))
    stats = (
        inn1.groupby(["venue", "toss_decision"])
        .agg(
            matches=("match_id", "nunique"),
            toss_win_rate=("toss_win_match_win", "mean"),
        )
        .round(3)
        .reset_index()
    )
    stats["toss_win_pct"] = (stats["toss_win_rate"] * 100).round(1)
    stats["low_sample"] = stats["matches"] < MIN_MATCHES
    return stats


def render_toss_strategy(df: pd.DataFrame, selected_venues: list[str]) -> None:
    stats = toss_strategy_stats(df)

    if selected_venues:
        stats = stats[stats["venue"].isin(selected_venues)]

    if stats.empty:
        st.warning("No data for the selected filters.")
        return

    low_sample = (
        stats[stats["low_sample"]][["venue", "toss_decision"]]
        .apply(lambda r: f"{r['venue']} ({r['toss_decision']})", axis=1)
        .tolist()
    )
    if low_sample:
        st.caption(
            f"Small sample (<{MIN_MATCHES} matches) — interpret with caution: "
            + ", ".join(low_sample)
        )

    # Sort venues by the gap between bat and field win rates for readability
    venue_order = (
        stats.pivot_table(index="venue", columns="toss_decision", values="toss_win_pct")
        .fillna(0)
        .assign(gap=lambda x: abs(x.get("bat", 0) - x.get("field", 0)))
        .sort_values("gap", ascending=False)
        .index.tolist()
    )

    fig = px.bar(
        stats,
        x="venue",
        y="toss_win_pct",
        color="toss_decision",
        barmode="group",
        category_orders={"venue": venue_order},
        color_discrete_map={"bat": "#2196F3", "field": "#FF9800"},
        labels={
            "venue": "Venue",
            "toss_win_pct": "Win Rate (%)",
            "toss_decision": "Toss Decision",
        },
        title="Toss Win → Match Win Rate by Venue & Decision",
        height=500,
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_range=[0, 100],
        legend_title="Toss Decision",
    )
    fig.add_hline(y=50, line_dash="dot", line_color="grey", annotation_text="50%")
    st.plotly_chart(fig, use_container_width=True)

    display_cols = {
        "venue": "Venue",
        "toss_decision": "Decision",
        "matches": "Matches",
        "toss_win_pct": "Win Rate (%)",
    }
    st.dataframe(
        stats[list(display_cols.keys())].rename(columns=display_cols),
        use_container_width=True,
        hide_index=True,
    )
