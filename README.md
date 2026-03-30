# IPL Venue Strategy & Insights Tool

An interactive analytics dashboard for cricket fans and analysts to explore how different IPL stadiums play, how teams have evolved across 16+ seasons, and what statistical patterns separate winning sides from losing ones — all powered by a single CSV file and zero internet dependency.

---

## Overview

The Indian Premier League spans **17 seasons (2008–2024)**, **39 distinct venues**, and more than **1,000 regulation matches**. Raw scorecards tell you who won; this tool tells you *why venues matter, when to bat first, and how the game has changed*.

Every chart is driven live from `ipl_2008_2024_complete.csv` — no database, no API calls, no pre-aggregated summaries. Filters applied in the sidebar instantly recompute every tab.

---

## Features

### 1. Venue Comparison
Compare average first-innings scores and run rates across stadiums.

- Bar chart of all-time average 1st-innings score per venue, colour-coded by run rate (green = fast, red = slow)
- **Year-by-year line chart** — select venues in the sidebar to see how average scores at each ground have shifted season by season
- Pivot table with season × venue breakdowns
- Venues with fewer than 10 matches flagged as small sample

### 2. Toss Strategy
Should you bat or field first at a given ground?

- Grouped bar chart showing the win rate for "bat" vs "field" decisions at every venue
- Venues sorted by the gap between the two decisions — largest advantages shown first
- 50% reference line to instantly spot where one decision dominates
- Powered by the pre-computed `toss_win_match_win` column — no double-counting

### 3. Phase Analysis
Where are the "Powerplay Paradises" and "Death Dens"?

- Scatter plot of powerplay run rate (overs 1–6) vs death-over run rate (overs 17–20), sized by match count
- Automatic quadrant classification based on the median split of both axes:
  - **Powerplay Paradise** — high scoring in the first 6 overs
  - **Death Dens** — high scoring at the death
  - **Powerplay Paradise / Death Dens** — high scoring throughout
  - **Bowler's Ground** — below-median run rates in both phases
- All phase rates shown as runs per over, never raw totals

### 4. Head-to-Head
The complete record between any two franchises.

- Summary metrics: total matches, Team A wins, Team B wins, no results
- Win-share donut chart for decided matches
- Season-by-season grouped bar chart of wins
- **Top 10 Player of the Match** performers in that specific rivalry, ranked by award count

### 5. Dominance Map
Which team owns which ground?

- YlOrRd heat map — top 20 venues (rows) × top 12 teams (columns)
- Toggle between **raw win count** and **win % at venue** to control for grounds that host more matches for certain franchises
- Expandable raw data table for exact numbers

### 6. Trends Over Time
How has IPL cricket changed year by year?

- Dual-axis line chart with era bands (Founding 2008–11 / Expansion 2012–15 / Modern 2016–19 / Post-COVID 2020–24)
- Overlay any combination of: Avg Run Rate, Avg Sixes/Innings, Avg Fours/Innings, Avg Score, Dot Ball %
- Quantifies the T20 evolution — sixes per innings has nearly doubled from 4.6 (2008) to 9.2 (2024)

### 7. Team DNA
How has a franchise's batting identity evolved?

- **Season-by-season line chart** for any metric: run rate, sixes, fours, score, powerplay run rate, death run rate, dot ball %
- **Era radar / spider chart** — overlays the team's normalised batting profile across all four eras to show style shifts visually
- Raw era averages table for exact figures

### 8. Dot Ball Pressure
Do fewer dot balls actually win matches?

- **Win Rate by Bucket** — bar chart of batting-first win rate split by dot-ball % buckets (<30%, 30–35%, … 50%+), with green/red colour scale
- **Distribution** — box or violin chart comparing dot ball % for batting-first winners vs losers
- **Scatter** — dot ball % vs run rate with separate numpy regression lines per outcome; confirms that winners score faster *at every dot-ball level*

---

## Sidebar Filters

All filters apply globally to every tab simultaneously.

| Filter | Default | Effect |
|---|---|---|
| Season range slider | 2008–2024 | Restricts all data to the selected seasons |
| Exclude DLS matches | On | Removes 42 D/L rows whose phase stats are unreliable |
| Exclude neutral venues | Off | Optionally removes 2009 (South Africa), 2014, 2020–21 (UAE) seasons |
| Venue multi-select | All | Narrows venue charts to selected stadiums; drives year-by-year line in Venue Comparison |

A warning banner appears if DLS matches are re-included.

---

## Installation

**Prerequisites:** Python 3.9 or later

```bash
# Clone or copy the project folder to your machine
cd D:/IPL

# Install dependencies
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`):
```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.20.0
numpy>=1.26.0
```

---

## Running the App

```bash
# From the D:/IPL directory
python -m streamlit run app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

> **Note:** Use `python -m streamlit` rather than `streamlit` directly if the `streamlit` command is not on your system PATH.

---

## Verifying the Data

Run the built-in assertion suite to confirm the CSV loaded and normalised correctly:

```bash
cd D:/IPL
PYTHONPATH=. python data/loader.py
```

Expected output:
```
Rows: 2145 | Matches: 1074 | Venues: 39
All data assertions passed.
```

---

## Project Structure

```
D:/IPL/
├── ipl_2008_2024_complete.csv   # Single source of truth — never modified
├── app.py                       # Streamlit entry point; sidebar + 8 tabs
│
├── data/
│   └── loader.py                # load_data() with caching, normalisation,
│                                #   and dev-mode assertions
│
├── features/
│   ├── venue_comparison.py      # Tab 1 — all-time + year-by-year scores
│   ├── toss_strategy.py         # Tab 2 — bat vs field win rates
│   ├── phase_analysis.py        # Tab 3 — powerplay / death quadrant scatter
│   ├── head_to_head.py          # Tab 4 — H2H record + top performers
│   ├── dominance_map.py         # Tab 5 — team × venue win heatmap
│   ├── trends.py                # Tab 6 — league-wide season trends
│   ├── team_dna.py              # Tab 7 — team batting evolution + radar
│   └── dot_ball_pressure.py     # Tab 8 — dot ball % vs win probability
│
└── utils/
    ├── venue_aliases.py         # 58 raw → 39 canonical venue names;
    │                            #   franchise rename map
    └── filters.py               # regulation_innings / first_innings /
                                 #   exclude_no_result helpers
```

---

## Data Notes

| Topic | Detail |
|---|---|
| Row structure | One row per innings per match — each `match_id` appears twice for regulation play |
| Match count | 1,074 regulation matches after excluding DLS (default) |
| Venue names | 58 raw strings normalised to 39 canonical names at load time |
| Super overs | Innings 3–6 excluded by default; they represent at most 7 balls |
| Team names | Delhi Daredevils → Delhi Capitals, Kings XI Punjab → Punjab Kings, etc. |
| DLS matches | 42 rows; excluded by default because death-over stats are truncated |
| No-result matches | 19 matches with empty `winner`; excluded from all win-rate calculations |
| Neutral seasons | 2009 (South Africa), 2014, 2020, 2021 (UAE) — toggle available in sidebar |
| Phase columns | `powerplay_runs` and `death_over_runs` are raw totals; divided by 6 and 4 for display |
| Season column | Stored as float in CSV (`2008.0`) — cast to int at load time |

---

## Key Findings (all seasons, DLS excluded)

- **Highest-scoring ground:** Wankhede Stadium, Mumbai (~165 avg 1st-innings score in recent seasons)
- **Biggest toss advantage:** Several grounds show 15–20 percentage point differences between bat and field win rates
- **Sixes explosion:** League-wide average sixes per innings grew from **4.6 (2008)** to **9.2 (2024)**
- **Dot ball signal:** Batting-first winners average **36.8%** dot balls vs **40.7%** for losing sides — a consistent ~4 percentage point gap across the dataset
- **CSK vs MI (the great rivalry):** 37 meetings; MI lead 20–17 across all seasons

---

## Tech Stack

| Layer | Library |
|---|---|
| UI & server | Streamlit 1.55+ |
| Data wrangling | Pandas 2.0+, NumPy 1.26+ |
| Charts | Plotly Express + Graph Objects |
| Data source | `ipl_2008_2024_complete.csv` (local, read-only) |
