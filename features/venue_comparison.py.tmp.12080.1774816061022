import pandas as pd
import plotly.express as px
import streamlit as st

from utils.filters import first_innings

MIN_MATCHES = 10


def venue_batting_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate batting stats per venue using innings-1 rows only.
    Returns one row per venue, sorted by avg_score descending."""
    inn1 = first_innings(df)
    stats = (
        inn1.groupby("venue")
        .agg(
            matches=("match_id", "nunique"),
            avg_score=("total_runs", "mean"),
            avg_run_rate=("run_rate", "mean"),
            avg_fours=("boundaries_4", "mean"),
            avg_sixes=("boundaries_6", "mean"),
            avg_dot_pct=("dot_ball_pct", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("avg_score", ascending=False)
    )
    stats["low_sample"] = stats["matches"] < MIN_MATCHES
    return stats


def venue_season_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Average 1st-innings score per venue per season."""
    inn1 = first_innings(df)
    return (
        inn1.groupby(["venue", "season"])
        .agg(
            matches=("match_id", "nunique"),
            avg_score=("total_runs", "mean"),
        )
        .round(2)
        .reset_index()
    )


def render_venue_comparison(df: pd.DataFrame, selected_venues: list[str]) -> None:
    stats = venue_batting_stats(df)

    if selected_venues:
        stats = stats[stats["venue"].isin(selected_venues)]

    if stats.empty:
        st.warning("No data for the selected filters.")
        return

    low_sample = stats[stats["low_sample"]]["venue"].tolist()
    if low_sample:
        st.caption(
            f"Small sample (<{MIN_MATCHES} matches) — interpret with caution: "
            + ", ".join(low_sample)
        )

    # ── Overall averages bar chart ────────────────────────────────────────────
    fig = px.bar(
        stats,
        x="venue",
        y="avg_score",
        color="avg_run_rate",
        color_continuous_scale="RdYlGn",
        labels={
            "venue": "Venue",
            "avg_score": "Avg 1st-innings Score",
            "avg_run_rate": "Avg Run Rate",
        },
        title="Average 1st-innings Score by Venue (all-time)",
        height=500,
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        coloraxis_colorbar_title="Run Rate",
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Year-by-year average score ────────────────────────────────────────────
    st.markdown("#### Average Score by Year")

    season_data = venue_season_stats(df)
    if selected_venues:
        season_data = season_data[season_data["venue"].isin(selected_venues)]

    if season_data.empty:
        st.info("No season-level data for the current selection.")
    else:
        # Use sidebar-selected venues directly; fall back to top 6 by match count
        if selected_venues:
            chart_venues = selected_venues
        else:
            top6 = (
                venue_batting_stats(df)
                .nlargest(6, "matches")["venue"]
                .tolist()
            )
            chart_venues = top6
            st.caption("Showing top 6 venues by match count. Select specific venues in the sidebar to compare others.")

        season_plot = season_data[season_data["venue"].isin(chart_venues)]

        fig_season = px.line(
            season_plot,
            x="season",
            y="avg_score",
            color="venue",
            markers=True,
            labels={
                "season": "Season",
                "avg_score": "Avg 1st-innings Score",
                "venue": "Venue",
            },
            title="Average 1st-innings Score per Venue per Year",
            height=500,
        )
        fig_season.update_layout(
            xaxis=dict(tickmode="linear", dtick=1, tickangle=-45),
            legend=dict(orientation="h", y=-0.3),
        )
        fig_season.update_traces(marker=dict(size=7))
        st.plotly_chart(fig_season, use_container_width=True)

        with st.expander("Year-by-year data table"):
            pivot = (
                season_data[season_data["venue"].isin(chart_venues)]
                .pivot_table(index="venue", columns="season", values="avg_score")
                .round(1)
            )
            pivot.columns = pivot.columns.astype(str)
            st.dataframe(pivot, use_container_width=True)

    st.divider()

    display_cols = {
        "venue": "Venue",
        "matches": "Matches",
        "avg_score": "Avg Score",
        "avg_run_rate": "Avg RR",
        "avg_fours": "Avg 4s",
        "avg_sixes": "Avg 6s",
        "avg_dot_pct": "Dot Ball %",
    }
    st.dataframe(
        stats[list(display_cols.keys())].rename(columns=display_cols),
        use_container_width=True,
        hide_index=True,
    )
