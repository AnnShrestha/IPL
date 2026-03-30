import streamlit as st

from data.loader import load_data
from features.venue_comparison import render_venue_comparison
from features.toss_strategy import render_toss_strategy
from features.phase_analysis import render_phase_analysis
from features.head_to_head import render_head_to_head
from features.dominance_map import render_dominance_map
from features.trends import render_trends
from features.team_dna import render_team_dna
from features.dot_ball_pressure import render_dot_ball_pressure

st.set_page_config(
    page_title="IPL Venue Strategy & Insights",
    page_icon="🏏",
    layout="wide",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🏏 Filters")

    season_range = st.slider(
        "Seasons",
        min_value=2008,
        max_value=2024,
        value=(2008, 2024),
        step=1,
    )

    exclude_dl = st.toggle("Exclude DLS matches", value=True)
    exclude_neutral = st.toggle(
        "Exclude neutral venues (2009 / 2014 / 2020–21)",
        value=False,
    )

    # Load data with current toggle state so the venue list is accurate
    df_full = load_data(
        exclude_dl=exclude_dl,
        exclude_neutral=exclude_neutral,
        regulation_only=True,
    )

    # Apply season filter
    df = df_full[
        df_full["season"].between(season_range[0], season_range[1])
    ].copy()

    all_venues = sorted(df["venue"].unique().tolist())
    selected_venues = st.multiselect(
        "Venues (leave blank for all)",
        options=all_venues,
        default=[],
    )

    all_teams = sorted(
        set(df["batting_team"].unique()) | set(df["bowling_team"].unique())
    )

    st.caption(
        f"{df['match_id'].nunique()} matches · "
        f"{df['venue'].nunique()} venues · "
        f"Seasons {season_range[0]}–{season_range[1]}"
    )

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("IPL Venue Strategy & Insights")
st.markdown(
    "Explore how different stadiums play across 16+ seasons of IPL cricket (2008–2024)."
)

if not exclude_dl:
    st.warning(
        "DLS matches included — death-over phase statistics may be unreliable "
        "for matches where the second innings was shortened."
    )

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Venue Comparison", "Toss Strategy", "Phase Analysis",
    "Head-to-Head", "Dominance Map",
    "Trends", "Team DNA", "Dot Ball Pressure",
])

with tab1:
    st.subheader("Venue Comparison")
    st.markdown(
        "Average 1st-innings scores and run rates across venues. "
        "Color intensity reflects run rate — greener = faster scoring."
    )
    render_venue_comparison(df, selected_venues)

with tab2:
    st.subheader("Toss Strategy")
    st.markdown(
        "Win rate when the toss winner chose to **bat** vs **field** at each venue. "
        "Bars above 50% indicate the decision gives a meaningful advantage."
    )
    render_toss_strategy(df, selected_venues)

with tab3:
    st.subheader("Phase Analysis")
    st.markdown(
        "Powerplay run rate (overs 1–6) vs death-over run rate (overs 17–20). "
        "Bubble size = number of matches. Quadrants reveal each ground's character."
    )
    render_phase_analysis(df, selected_venues)

with tab4:
    st.subheader("Head-to-Head")
    st.markdown(
        "Historical win/loss record between two teams, season-by-season breakdown, "
        "and the top Player of the Match performers in that rivalry."
    )
    render_head_to_head(df, all_teams)

with tab5:
    st.subheader("Dominance Map")
    st.markdown(
        "Heat map of wins per team at each venue. Toggle between raw win counts "
        "and win percentage to control for unequal home-ground exposure."
    )
    render_dominance_map(df)

with tab6:
    st.subheader("Trends Over Time")
    st.markdown(
        "League-wide evolution of run rates, sixes, boundaries, and dot balls "
        "across all IPL seasons. Era bands show how the game has changed."
    )
    render_trends(df)

with tab7:
    st.subheader("Team DNA")
    st.markdown(
        "How a team's batting style has evolved across eras — radar chart for "
        "era-by-era comparison and a season-by-season trend line."
    )
    render_team_dna(df, all_teams)

with tab8:
    st.subheader("Dot Ball Pressure")
    st.markdown(
        "Does restricting dot balls correlate with winning? "
        "Win rate by dot-ball bucket, distribution comparisons, and a scatter of "
        "dot ball % vs run rate for batting-first innings."
    )
    render_dot_ball_pressure(df)
