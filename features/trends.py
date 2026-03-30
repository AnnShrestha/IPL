import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.filters import first_innings


def _season_trends(df: pd.DataFrame) -> pd.DataFrame:
    """League-wide averages per season, computed from innings-1 rows."""
    inn1 = first_innings(df)
    return (
        inn1.groupby("season")
        .agg(
            matches=("match_id", "nunique"),
            avg_run_rate=("run_rate", "mean"),
            avg_sixes=("boundaries_6", "mean"),
            avg_fours=("boundaries_4", "mean"),
            avg_total=("total_runs", "mean"),
            avg_dot_pct=("dot_ball_pct", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("season")
    )


def render_trends(df: pd.DataFrame) -> None:
    trends = _season_trends(df)

    if trends.empty or len(trends) < 2:
        st.warning("Not enough seasons in the current filter range to plot trends.")
        return

    metrics = st.multiselect(
        "Metrics to overlay",
        options=["Avg Run Rate", "Avg Sixes / Innings", "Avg Fours / Innings", "Avg Score", "Dot Ball %"],
        default=["Avg Run Rate", "Avg Sixes / Innings"],
        key="trend_metrics",
    )

    col_map = {
        "Avg Run Rate": ("avg_run_rate", "#FF9800"),
        "Avg Sixes / Innings": ("avg_sixes", "#E91E63"),
        "Avg Fours / Innings": ("avg_fours", "#2196F3"),
        "Avg Score": ("avg_total", "#4CAF50"),
        "Dot Ball %": ("avg_dot_pct", "#9C27B0"),
    }

    if not metrics:
        st.info("Select at least one metric above.")
        return

    # Dual-axis: first metric on left y-axis, rest on right (different scales)
    fig = go.Figure()

    for i, label in enumerate(metrics):
        col, color = col_map[label]
        use_right = i > 0
        fig.add_trace(go.Scatter(
            x=trends["season"],
            y=trends[col],
            mode="lines+markers",
            name=label,
            line=dict(color=color, width=2),
            marker=dict(size=7),
            yaxis="y2" if use_right else "y",
        ))

    # Shaded bands for eras
    era_bands = [
        (2008, 2011, "rgba(200,200,200,0.15)", "Founding Era"),
        (2012, 2015, "rgba(180,200,220,0.15)", "Expansion"),
        (2016, 2019, "rgba(220,200,180,0.15)", "Modern"),
        (2020, 2024, "rgba(200,220,200,0.15)", "Post-COVID"),
    ]
    for start, end, fill, era_label in era_bands:
        fig.add_vrect(
            x0=start - 0.5, x1=end + 0.5,
            fillcolor=fill,
            line_width=0,
            annotation_text=era_label,
            annotation_position="top left",
            annotation_font_size=10,
            annotation_font_color="grey",
        )

    primary_label = metrics[0]
    secondary_label = metrics[1] if len(metrics) > 1 else ""

    fig.update_layout(
        title="League-Wide Trends by Season",
        xaxis=dict(title="Season", tickmode="linear", dtick=1, tickangle=-45),
        yaxis=dict(title=primary_label, side="left"),
        yaxis2=dict(
            title=secondary_label,
            side="right",
            overlaying="y",
            showgrid=False,
        ),
        legend=dict(orientation="h", y=-0.2),
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Season data table"):
        display = trends.rename(columns={
            "season": "Season", "matches": "Matches",
            "avg_run_rate": "Avg RR", "avg_sixes": "Avg 6s",
            "avg_fours": "Avg 4s", "avg_total": "Avg Score",
            "avg_dot_pct": "Dot Ball %",
        })
        st.dataframe(display, use_container_width=True, hide_index=True)
