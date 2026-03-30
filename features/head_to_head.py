import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.filters import first_innings, exclude_no_result


def _h2h_matches(df: pd.DataFrame, team_a: str, team_b: str) -> pd.DataFrame:
    """Return innings-1 rows for matches strictly between team_a and team_b."""
    inn1 = first_innings(df)
    both = {team_a, team_b}
    return inn1[
        inn1["batting_team"].isin(both) & inn1["bowling_team"].isin(both)
    ].copy()


def render_head_to_head(df: pd.DataFrame, all_teams: list[str]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Team A", all_teams, index=all_teams.index("Chennai Super Kings") if "Chennai Super Kings" in all_teams else 0, key="h2h_a")
    with col2:
        default_b = "Mumbai Indians" if "Mumbai Indians" in all_teams else (all_teams[1] if len(all_teams) > 1 else all_teams[0])
        team_b = st.selectbox("Team B", all_teams, index=all_teams.index(default_b), key="h2h_b")

    if team_a == team_b:
        st.warning("Select two different teams.")
        return

    matches = _h2h_matches(df, team_a, team_b)

    if matches.empty:
        st.info("No head-to-head matches found for the current filters.")
        return

    total = len(matches)
    a_wins = (matches["winner"] == team_a).sum()
    b_wins = (matches["winner"] == team_b).sum()
    no_result = (matches["winner"] == "").sum()

    # ── Summary metrics ──────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Matches", total)
    m2.metric(f"{team_a} wins", int(a_wins))
    m3.metric(f"{team_b} wins", int(b_wins))
    m4.metric("No result", int(no_result))

    st.divider()
    left, right = st.columns(2)

    # ── Win-share donut ───────────────────────────────────────────────────────
    with left:
        decided = matches[matches["winner"] != ""]
        pie_data = pd.DataFrame({
            "Team": [team_a, team_b],
            "Wins": [a_wins, b_wins],
        })
        fig_pie = px.pie(
            pie_data,
            names="Team",
            values="Wins",
            hole=0.5,
            color="Team",
            color_discrete_sequence=["#2196F3", "#FF9800"],
            title=f"Win Share ({len(decided)} decided matches)",
        )
        fig_pie.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Wins per season ───────────────────────────────────────────────────────
    with right:
        season_wins = (
            matches[matches["winner"].isin([team_a, team_b])]
            .groupby(["season", "winner"])
            .size()
            .reset_index(name="wins")
        )
        fig_season = px.bar(
            season_wins,
            x="season",
            y="wins",
            color="winner",
            barmode="group",
            color_discrete_map={team_a: "#2196F3", team_b: "#FF9800"},
            labels={"season": "Season", "wins": "Wins", "winner": "Team"},
            title="Wins per Season",
            height=350,
        )
        fig_season.update_layout(xaxis=dict(tickmode="linear", dtick=1))
        st.plotly_chart(fig_season, use_container_width=True)

    # ── Top Performers ────────────────────────────────────────────────────────
    st.subheader(f"Top Performers — {team_a} vs {team_b}")
    st.markdown("Most frequent Player of the Match awards in this rivalry.")

    pom = (
        matches[matches["player_of_match"].notna() & (matches["player_of_match"] != "")]
        ["player_of_match"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    pom.columns = ["Player", "Awards"]

    if pom.empty:
        st.info("No Player of the Match data available.")
        return

    fig_pom = px.bar(
        pom,
        x="Awards",
        y="Player",
        orientation="h",
        color="Awards",
        color_continuous_scale="Blues",
        labels={"Awards": "Player of the Match Awards", "Player": ""},
        title=f"Top 10 Players — {team_a} vs {team_b}",
        height=400,
    )
    fig_pom.update_layout(
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_pom, use_container_width=True)
