import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.filters import first_innings, exclude_no_result

BUCKET_EDGES = [0, 30, 35, 40, 45, 50, 100]
BUCKET_LABELS = ["<30%", "30–35%", "35–40%", "40–45%", "45–50%", "50%+"]


def _dot_ball_pressure_data(df: pd.DataFrame) -> pd.DataFrame:
    """For each innings-1 row (one per match), flag whether the batting team won."""
    base = exclude_no_result(first_innings(df))
    out = base[["match_id", "batting_team", "bowling_team", "winner",
                "dot_ball_pct", "run_rate", "total_runs", "season"]].copy()
    out["batting_won"] = (out["batting_team"] == out["winner"]).astype(int)
    out["dot_bucket"] = pd.cut(
        out["dot_ball_pct"],
        bins=BUCKET_EDGES,
        labels=BUCKET_LABELS,
        right=False,
    )
    return out


def render_dot_ball_pressure(df: pd.DataFrame) -> None:
    data = _dot_ball_pressure_data(df)

    if data.empty:
        st.warning("No data for the selected filters.")
        return

    tab_a, tab_b, tab_c = st.tabs(["Win Rate by Bucket", "Distribution: Winners vs Losers", "Scatter"])

    # ── Tab A: Win rate per dot-ball bucket ───────────────────────────────────
    with tab_a:
        bucket_stats = (
            data.groupby("dot_bucket", observed=True)
            .agg(matches=("match_id", "count"), win_rate=("batting_won", "mean"))
            .reset_index()
        )
        bucket_stats["win_pct"] = (bucket_stats["win_rate"] * 100).round(1)

        fig_bucket = px.bar(
            bucket_stats,
            x="dot_bucket",
            y="win_pct",
            text="win_pct",
            color="win_pct",
            color_continuous_scale="RdYlGn",
            range_color=[30, 70],
            labels={"dot_bucket": "Dot Ball %", "win_pct": "Batting-First Win Rate (%)"},
            title="Does Playing Fewer Dot Balls Win Matches? (Batting First)",
            height=450,
        )
        fig_bucket.add_hline(y=50, line_dash="dot", line_color="grey", annotation_text="50%")
        fig_bucket.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_bucket.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bucket, use_container_width=True)

        st.caption(
            "Win rate for the team **batting first**. A value below 50% in high dot-ball "
            "buckets suggests dot-ball pressure favours the chasing team."
        )

        m1, m2 = st.columns(2)
        winners_dot = data[data["batting_won"] == 1]["dot_ball_pct"].mean()
        losers_dot = data[data["batting_won"] == 0]["dot_ball_pct"].mean()
        m1.metric("Avg dot ball % — batting-first winners", f"{winners_dot:.1f}%")
        m2.metric("Avg dot ball % — batting-first losers", f"{losers_dot:.1f}%")

    # ── Tab B: Box / violin distribution ─────────────────────────────────────
    with tab_b:
        data["outcome"] = data["batting_won"].map({1: "Won", 0: "Lost"})
        chart_type = st.radio("Chart type", ["Box", "Violin"], horizontal=True, key="db_chart")

        if chart_type == "Violin":
            fig_dist = px.violin(
                data,
                x="outcome",
                y="dot_ball_pct",
                color="outcome",
                box=True,
                points="outliers",
                color_discrete_map={"Won": "#4CAF50", "Lost": "#F44336"},
                labels={"outcome": "Batting-First Outcome", "dot_ball_pct": "Dot Ball %"},
                title="Dot Ball % Distribution — Batting-First Winners vs Losers",
                height=450,
            )
        else:
            fig_dist = px.box(
                data,
                x="outcome",
                y="dot_ball_pct",
                color="outcome",
                points="outliers",
                color_discrete_map={"Won": "#4CAF50", "Lost": "#F44336"},
                labels={"outcome": "Batting-First Outcome", "dot_ball_pct": "Dot Ball %"},
                title="Dot Ball % Distribution — Batting-First Winners vs Losers",
                height=450,
            )

        st.plotly_chart(fig_dist, use_container_width=True)

    # ── Tab C: Scatter — dot ball % vs run rate, coloured by outcome ─────────
    with tab_c:
        sample = data.sample(min(len(data), 600), random_state=42) if len(data) > 600 else data

        color_map = {"Won": "#4CAF50", "Lost": "#F44336"}
        fig_scatter = px.scatter(
            sample,
            x="dot_ball_pct",
            y="run_rate",
            color="outcome",
            opacity=0.55,
            color_discrete_map=color_map,
            labels={
                "dot_ball_pct": "Dot Ball %",
                "run_rate": "Run Rate",
                "outcome": "Outcome",
            },
            title="Dot Ball % vs Run Rate (batting-first innings)",
            height=450,
        )

        # Add numpy-based linear trendlines per outcome (no statsmodels needed)
        x_range = np.linspace(data["dot_ball_pct"].min(), data["dot_ball_pct"].max(), 100)
        for outcome, color in color_map.items():
            subset = data[data["outcome"] == outcome]
            if len(subset) < 2:
                continue
            coeffs = np.polyfit(subset["dot_ball_pct"], subset["run_rate"], 1)
            fig_scatter.add_trace(go.Scatter(
                x=x_range,
                y=np.polyval(coeffs, x_range),
                mode="lines",
                name=f"{outcome} trend",
                line=dict(color=color, width=2, dash="dash"),
                showlegend=True,
            ))

        st.plotly_chart(fig_scatter, use_container_width=True)
        if len(data) > 600:
            st.caption(f"Scatter shows a random sample of 600 / {len(data)} innings for clarity.")
