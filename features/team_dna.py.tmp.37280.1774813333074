import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.filters import first_innings

ERAS = {
    "Founding (2008–11)": (2008, 2011),
    "Expansion (2012–15)": (2012, 2015),
    "Modern (2016–19)": (2016, 2019),
    "Post-COVID (2020–24)": (2020, 2024),
}

# Radar axis labels and the underlying computed column names
RADAR_AXES = [
    "Run Rate",
    "Sixes / Inn",
    "Fours / Inn",
    "PP Run Rate",
    "Death RR",
    "Score",
]


def _team_batting(df: pd.DataFrame, team: str) -> pd.DataFrame:
    """All innings where the selected team batted (any innings number)."""
    return df[df["batting_team"] == team].copy()


def _season_stats(batting: pd.DataFrame) -> pd.DataFrame:
    agg = (
        batting.groupby("season")
        .agg(
            innings=("match_id", "count"),
            avg_run_rate=("run_rate", "mean"),
            avg_sixes=("boundaries_6", "mean"),
            avg_fours=("boundaries_4", "mean"),
            avg_score=("total_runs", "mean"),
            avg_pp_runs=("powerplay_runs", "mean"),
            avg_death_runs=("death_over_runs", "mean"),
            avg_dot_pct=("dot_ball_pct", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("season")
    )
    agg["pp_run_rate"] = (agg["avg_pp_runs"] / 6).round(2)
    agg["death_run_rate"] = (agg["avg_death_runs"] / 4).round(2)
    return agg


def _era_stats(batting: pd.DataFrame) -> dict[str, pd.Series]:
    result = {}
    for era_name, (start, end) in ERAS.items():
        era_data = batting[batting["season"].between(start, end)]
        if era_data.empty:
            continue
        result[era_name] = pd.Series({
            "Run Rate": era_data["run_rate"].mean(),
            "Sixes / Inn": era_data["boundaries_6"].mean(),
            "Fours / Inn": era_data["boundaries_4"].mean(),
            "PP Run Rate": (era_data["powerplay_runs"] / 6).mean(),
            "Death RR": (era_data["death_over_runs"] / 4).mean(),
            "Score": era_data["total_runs"].mean(),
        }).round(2)
    return result


def _normalise_radar(era_dict: dict[str, pd.Series]) -> dict[str, list[float]]:
    """Min-max scale each axis to [0, 1] across all eras for radar display."""
    all_vals = pd.DataFrame(era_dict).T
    min_v = all_vals.min()
    max_v = all_vals.max()
    rng = (max_v - min_v).replace(0, 1)  # avoid divide-by-zero on flat metrics
    normalised = {}
    for era, series in era_dict.items():
        normalised[era] = ((series - min_v) / rng).tolist()
    return normalised


def render_team_dna(df: pd.DataFrame, all_teams: list[str]) -> None:
    team = st.selectbox(
        "Select team",
        all_teams,
        index=all_teams.index("Mumbai Indians") if "Mumbai Indians" in all_teams else 0,
        key="dna_team",
    )

    batting = _team_batting(df, team)
    if batting.empty:
        st.warning(f"No batting data for {team} in the current filter range.")
        return

    season_stats = _season_stats(batting)
    era_dict = _era_stats(batting)

    left, right = st.columns(2)

    # ── Season-by-season line chart ───────────────────────────────────────────
    with left:
        metric_opt = st.selectbox(
            "Season trend metric",
            ["avg_run_rate", "avg_sixes", "avg_fours", "avg_score", "pp_run_rate", "death_run_rate", "avg_dot_pct"],
            format_func=lambda c: {
                "avg_run_rate": "Run Rate",
                "avg_sixes": "Sixes / Inn",
                "avg_fours": "Fours / Inn",
                "avg_score": "Avg Score",
                "pp_run_rate": "PP Run Rate",
                "death_run_rate": "Death Run Rate",
                "avg_dot_pct": "Dot Ball %",
            }[c],
            key="dna_metric",
        )

        fig_line = px.line(
            season_stats,
            x="season",
            y=metric_opt,
            markers=True,
            labels={"season": "Season", metric_opt: metric_opt.replace("_", " ").title()},
            title=f"{team} — Season-by-Season",
            height=380,
        )
        fig_line.update_traces(line_color="#FF9800", marker=dict(size=8))
        fig_line.update_layout(xaxis=dict(tickmode="linear", dtick=1, tickangle=-45))
        st.plotly_chart(fig_line, use_container_width=True)

    # ── Radar / spider chart across eras ──────────────────────────────────────
    with right:
        if len(era_dict) < 2:
            st.info("Need data from at least 2 eras to render radar chart.")
        else:
            normed = _normalise_radar(era_dict)
            axes = RADAR_AXES
            colors = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63"]

            fig_radar = go.Figure()
            for i, (era_name, values) in enumerate(normed.items()):
                # Close the polygon
                fig_radar.add_trace(go.Scatterpolar(
                    r=values + [values[0]],
                    theta=axes + [axes[0]],
                    fill="toself",
                    name=era_name,
                    line_color=colors[i % len(colors)],
                    fillcolor=colors[i % len(colors)].replace(")", ", 0.15)").replace("rgb", "rgba"),
                    opacity=0.8,
                ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1], tickfont_size=9),
                ),
                title=f"{team} — Batting DNA by Era",
                legend=dict(orientation="h", y=-0.15),
                height=380,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    # ── Era summary table ─────────────────────────────────────────────────────
    if era_dict:
        st.markdown("**Raw era averages**")
        era_df = pd.DataFrame(era_dict).T.reset_index().rename(columns={"index": "Era"})
        st.dataframe(era_df, use_container_width=True, hide_index=True)
