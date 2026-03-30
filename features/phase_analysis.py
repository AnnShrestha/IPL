import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.filters import first_innings

MIN_MATCHES = 10


def phase_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Per-venue powerplay and death-over rates using innings-1 rows.

    powerplay_runs and death_over_runs are raw totals in the CSV.
    Divide by 6 and 4 respectively to get per-over run rates.
    """
    inn1 = first_innings(df)
    agg = (
        inn1.groupby("venue")
        .agg(
            matches=("match_id", "nunique"),
            avg_pp_runs=("powerplay_runs", "mean"),
            avg_pp_wkts=("powerplay_wickets", "mean"),
            avg_death_runs=("death_over_runs", "mean"),
            avg_death_wkts=("death_over_wickets", "mean"),
        )
        .reset_index()
    )
    agg["pp_run_rate"] = (agg["avg_pp_runs"] / 6).round(2)
    agg["death_run_rate"] = (agg["avg_death_runs"] / 4).round(2)
    agg["low_sample"] = agg["matches"] < MIN_MATCHES
    return agg.sort_values("pp_run_rate", ascending=False)


def _quadrant_label(pp: float, death: float, pp_mid: float, death_mid: float) -> str:
    high_pp = pp >= pp_mid
    high_death = death >= death_mid
    if high_pp and high_death:
        return "Powerplay Paradise / Death Dens"
    if high_pp and not high_death:
        return "Powerplay Paradise"
    if not high_pp and high_death:
        return "Death Dens"
    return "Bowler's Ground"


def render_phase_analysis(df: pd.DataFrame, selected_venues: list[str]) -> None:
    stats = phase_stats(df)

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

    pp_mid = stats["pp_run_rate"].median()
    death_mid = stats["death_run_rate"].median()

    stats["quadrant"] = stats.apply(
        lambda r: _quadrant_label(r["pp_run_rate"], r["death_run_rate"], pp_mid, death_mid),
        axis=1,
    )

    quadrant_colors = {
        "Powerplay Paradise": "#4CAF50",
        "Powerplay Paradise / Death Dens": "#FF9800",
        "Death Dens": "#F44336",
        "Bowler's Ground": "#2196F3",
    }

    fig = px.scatter(
        stats,
        x="pp_run_rate",
        y="death_run_rate",
        size="matches",
        color="quadrant",
        color_discrete_map=quadrant_colors,
        text="venue",
        labels={
            "pp_run_rate": "Powerplay Run Rate (Runs/Over, Overs 1–6)",
            "death_run_rate": "Death Over Run Rate (Runs/Over, Overs 17–20)",
            "quadrant": "Venue Type",
            "matches": "Matches",
        },
        title="Phase Quadrant: Powerplay vs Death Overs by Venue",
        height=600,
    )
    fig.update_traces(textposition="top center", marker=dict(sizemin=8))

    # Median reference lines
    fig.add_vline(x=pp_mid, line_dash="dot", line_color="grey")
    fig.add_hline(y=death_mid, line_dash="dot", line_color="grey")

    # Quadrant labels in the four corners
    x_min, x_max = stats["pp_run_rate"].min(), stats["pp_run_rate"].max()
    y_min, y_max = stats["death_run_rate"].min(), stats["death_run_rate"].max()
    pad_x = (x_max - x_min) * 0.04
    pad_y = (y_max - y_min) * 0.04

    for label, x, y in [
        ("Powerplay Paradise", x_max - pad_x, y_min + pad_y),
        ("Powerplay Paradise\n/ Death Dens", x_max - pad_x, y_max - pad_y),
        ("Bowler's Ground", x_min + pad_x, y_min + pad_y),
        ("Death Dens", x_min + pad_x, y_max - pad_y),
    ]:
        fig.add_annotation(
            x=x, y=y, text=label,
            showarrow=False,
            font=dict(size=10, color="grey"),
            xanchor="center",
        )

    st.plotly_chart(fig, use_container_width=True)

    display_cols = {
        "venue": "Venue",
        "matches": "Matches",
        "pp_run_rate": "PP Run Rate",
        "avg_pp_wkts": "Avg PP Wkts",
        "death_run_rate": "Death Run Rate",
        "avg_death_wkts": "Avg Death Wkts",
        "quadrant": "Type",
    }
    st.dataframe(
        stats[list(display_cols.keys())].rename(columns=display_cols),
        use_container_width=True,
        hide_index=True,
    )
