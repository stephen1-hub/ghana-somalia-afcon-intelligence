
import json
import sqlite3
from pathlib import Path


import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# 1. CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "match_intelligence"
)

st.set_page_config(
    page_title="Ghana vs Somalia | Match Intelligence",
    page_icon="⚽",
    layout="wide"
)


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

st.sidebar.title("⚽ Match Intelligence")

st.sidebar.caption("Ghana vs Somalia | AFCON Qualifiers")

st.sidebar.divider()

st.sidebar.markdown("### Navigation")

st.sidebar.markdown(
    """
    - [Match Overview](#match-overview)
    - [Team Performance](#team-performance)
    - [Half-by-Half Analysis](#half-by-half-analysis)
    - [Player Intelligence](#player-intelligence)
    - [Match Timeline](#match-event-timeline)
    - [Analyst's Report](#analysts-match-report)
    """
)

st.sidebar.divider()

st.sidebar.markdown(
    "**Data Source**  \n"
    "FotMob"
)

st.sidebar.caption(
    "Built with Python, Pandas, Plotly and Streamlit."
)


# ==================================================
# 2. LOAD DATA
# ==================================================

# ==================================================
# 2. LOAD DATA FROM SQLITE
# ==================================================

DATABASE_PATH = (
    BASE_DIR
    / "data"
    / "database"
    / "ghana_somalia_intelligence.db"
)


@st.cache_data
def load_data():

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    with sqlite3.connect(DATABASE_PATH) as connection:

        # Load original nested JSON summary
        summary_record = pd.read_sql_query(
            "SELECT summary_json FROM match_intelligence_summary LIMIT 1",
            connection
        )

        if summary_record.empty:
            raise ValueError(
                "Match intelligence summary is missing."
            )

        summary = json.loads(
            summary_record.iloc[0]["summary_json"]
        )

        # Load dashboard datasets
        metrics = pd.read_sql_query(
            "SELECT * FROM match_intelligence_metrics",
            connection
        )

        half_performance = pd.read_sql_query(
            "SELECT * FROM half_performance_comparison",
            connection
        )

        timeline = pd.read_sql_query(
            "SELECT * FROM match_intelligence_timeline",
            connection
        )

        players = pd.read_sql_query(
            "SELECT * FROM match_intelligence_players",
            connection
        )

    return (
        summary,
        metrics,
        timeline,
        players,
        half_performance
    )


summary, metrics, timeline, players, half_performance = load_data()


@st.cache_data
def load_data():

    with open(
        DATA_DIR / "match_intelligence_summary.json",
        "r",
        encoding="utf-8"
    ) as file:
        summary = json.load(file)

    metrics = pd.read_csv(
        DATA_DIR / "match_intelligence_metrics.csv"
    )
    
    half_performance = pd.read_csv(
    BASE_DIR
    / "data"
    / "processed"
    / "half_performance_comparison.csv"
    )
    timeline = pd.read_csv(
        DATA_DIR / "match_intelligence_timeline.csv"
    )

    players = pd.read_csv(
        DATA_DIR / "match_intelligence_players.csv"
    )

    return summary, metrics, timeline, players, half_performance


summary, metrics, timeline, players, half_performance = load_data()



# ==================================================
# 3. MATCH INFORMATION
# ==================================================

match = summary["match_information"]

st.title(
    "⚽ Match Intelligence Dashboard",
    anchor="match-overview"
)

with st.container(border=True):

    # Competition and match status
    header_col1, header_col2 = st.columns([4, 1])

    with header_col1:
        st.caption(match["competition"])

    with header_col2:
        st.markdown(
            """
            <div style="
                text-align: right;
                color: #168447;
                font-weight: 600;
                font-size: 13px;
            ">
                ● FULL TIME
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Teams and score
    home_col, score_col, away_col = st.columns(
        [2, 1, 2],
        vertical_alignment="center"
    )

    
    
    # Ghana — Home team
    with home_col:
        st.markdown(
            """
            <div style="text-align:center; padding:15px 0;">
                <img src="https://flagcdn.com/w160/gh.png"
                     width="76"
                     style="border-radius:5px;">
                <div style="color:#168447;
                            font-size:12px;
                            font-weight:700;
                            letter-spacing:2px;
                            margin-top:12px;">
                    HOME
                </div>
                <div style="font-size:26px;
                            font-weight:700;
                            margin-top:8px;">
                    Ghana
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Centre scoreline
    with score_col:
        st.markdown(
            f"""
            <div style="text-align:center; padding:30px 0;">
                <div style="font-size:42px;
                            font-weight:800;
                            letter-spacing:4px;
                            white-space:nowrap;">
                    {match['home_score']} - {match['away_score']}
                </div>
                <div style="color:#168447;
                            font-size:12px;
                            font-weight:700;
                            margin-top:8px;">
                    FULL TIME
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Somalia — Away team
    with away_col:
        st.markdown(
            """
            <div style="text-align:center; padding:15px 0;">
                <img src="https://flagcdn.com/w160/so.png"
                     width="76"
                     style="border-radius:5px;">
                <div style="color:#777777;
                            font-size:12px;
                            font-weight:700;
                            letter-spacing:2px;
                            margin-top:12px;">
                    AWAY
                </div>
                <div style="font-size:26px;
                            font-weight:700;
                            margin-top:8px;">
                    Somalia
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ==================================================
# 4. KEY PERFORMANCE INDICATORS
# ==================================================

team_performance = summary["team_performance"]

possession = team_performance["possession"]
shots = team_performance["total_shots"]
shots_on_target = team_performance["shots_on_target"]
box_touches = team_performance["opposition_box_touches"]
pass_accuracy = team_performance["pass_accuracy"]

st.subheader("Match Performance")
st.caption("Full-time statistical comparison")

col1, col2, col3, col4, col5 = st.columns(5)

kpis = [
    ("Possession", possession),
    ("Total Shots", shots),
    ("Shots on Target", shots_on_target),
    ("Opposition Box Touches", box_touches),
    ("Pass Accuracy", pass_accuracy)
]

for col, (label, values) in zip(
    [col1, col2, col3, col4, col5], kpis
):
    if label in ["Possession", "Pass Accuracy"]:
        ghana_value = f"{values['Ghana']:.0f}%"
        somalia_value = f"{values['Somalia']:.0f}%"
    else:
        ghana_value = f"{values['Ghana']:.0f}"
        somalia_value = f"{values['Somalia']:.0f}"

    with col:
        st.metric(
            label,
            f"{ghana_value} : {somalia_value}"
        )
        st.caption("Ghana : Somalia")


# ==================================================
# 5. TEAM PERFORMANCE COMPARISON
# ==================================================

st.divider()

st.subheader(
    "Team Performance Comparison",
    anchor="team-performance"
)

st.dataframe(
    metrics,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# 6. INTERACTIVE COMPARISON CHARTS
# ==================================================

def create_comparison_chart(data, title):

    chart_data = data.melt(
        id_vars="Metric",
        value_vars=["Ghana", "Somalia"],
        var_name="Team",
        value_name="Value"
    )

    fig = px.bar(
        chart_data,
        x="Value",
        y="Metric",
        color="Team",
        barmode="group",
        orientation="h",
        text="Value",
        title=title,
        color_discrete_map={
            "Ghana": "#168447",
            "Somalia": "#A7DCC0"
        }
    )

    fig.update_layout(
        height=420,
        template="plotly_white",
        legend_title="Team",
        yaxis={"categoryorder": "total ascending"},
        margin=dict(
            l=20,
            r=40,
            t=60,
            b=20
        )
    )

    fig.update_traces(
        textposition="outside"
    )

    return fig


# -------------------------------
# 6A. ATTACKING PERFORMANCE
# -------------------------------

st.subheader("Attacking Performance")

attacking_metrics = [
    "Total shots",
    "Shots on target",
    "Shots inside box",
    "Opposition box touches",
    "Big chances",
    "Big chances missed"
]

attacking_data = metrics[
    metrics["Metric"].isin(attacking_metrics)
].copy()

if not attacking_data.empty:

    fig_attack = create_comparison_chart(
        attacking_data,
        "Ghana vs Somalia — Attacking Comparison"
    )

    st.plotly_chart(
        fig_attack,
        use_container_width=True
    )


# -------------------------------
# 6B. POSSESSION AND PASSING
# -------------------------------

st.subheader("Possession and Passing")

control_metrics = [
    "Possession (%)",
    "Pass accuracy (%)",
    "Shot accuracy (%)"
]

control_data = metrics[
    metrics["Metric"].isin(control_metrics)
].copy()

if not control_data.empty:

    fig_control = create_comparison_chart(
        control_data,
        "Ghana vs Somalia — Match Control"
    )

    st.plotly_chart(
        fig_control,
        use_container_width=True
    )


# -------------------------------
# 6C. DEFENSIVE PERFORMANCE
# -------------------------------

st.subheader("Defensive Performance")

defensive_metrics = [
    "Tackles",
    "Interceptions",
    "Clearances",
    "Blocks",
    "Fouls committed"
]

defensive_data = metrics[
    metrics["Metric"].isin(defensive_metrics)
].copy()

if not defensive_data.empty:

    fig_defence = create_comparison_chart(
        defensive_data,
        "Ghana vs Somalia — Defensive Comparison"
    )

    st.plotly_chart(
        fig_defence,
        use_container_width=True
    )



# ==================================================
# 7. FIRST-HALF VS SECOND-HALF ANALYSIS
# ==================================================

st.divider()

st.header(
    "First-Half vs Second-Half Analysis",
    anchor="half-by-half-analysis"
)

st.write(
    "How did Ghana and Somalia perform across the two halves?"
)

# Metrics available for comparison
half_metrics = [
    "Ball possession",
    "Total shots",
    "Shots on target",
    "Shots inside box",
    "Passes",
    "Accurate passes",
    "Tackles",
    "Interceptions",
    "Clearances"
]

half_data = half_performance[
    half_performance["metric"].isin(half_metrics)
].copy()

# Reshape data for Plotly
half_chart_data = half_data.melt(
    id_vars=["category", "metric"],
    value_vars=[
        "first_half_ghana",
        "first_half_somalia",
        "second_half_ghana",
        "second_half_somalia"
    ],
    var_name="Team_Period",
    value_name="Value"
)

# Extract team and match period
half_chart_data["Team"] = (
    half_chart_data["Team_Period"]
    .str.extract(r"(ghana|somalia)")[0]
    .str.title()
)

half_chart_data["Half"] = (
    half_chart_data["Team_Period"]
    .str.extract(r"(first_half|second_half)")[0]
    .map({
        "first_half": "First Half",
        "second_half": "Second Half"
    })
)

# Extract numeric values.
# For Accurate passes, values such as 269 (91%) become 269.
half_chart_data["Value"] = (
    half_chart_data["Value"]
    .astype(str)
    .str.extract(r"([-+]?\d*\.?\d+)")[0]
)

half_chart_data["Value"] = pd.to_numeric(
    half_chart_data["Value"],
    errors="coerce"
)

# Metric selector
selected_metric = st.selectbox(
    "Select a match metric",
    half_metrics,
    key="half_metric_selector"
)

selected_data = half_chart_data[
    half_chart_data["metric"] == selected_metric
].dropna(subset=["Value"]).copy()

# Display selected values for verification
if selected_data.empty:
    st.warning(
        f"No numerical data is available for {selected_metric}."
    )

else:
    # Keep the chart order consistent
    selected_data["Half"] = pd.Categorical(
        selected_data["Half"],
        categories=["First Half", "Second Half"],
        ordered=True
    )

    selected_data["Team"] = pd.Categorical(
        selected_data["Team"],
        categories=["Ghana", "Somalia"],
        ordered=True
    )

    fig_half = px.bar(
        selected_data,
        x="Half",
        y="Value",
        color="Team",
        barmode="group",
        text="Value",
        color_discrete_map={
            "Ghana": "#168447",
            "Somalia": "#A7DCC0"
        },
        category_orders={
            "Half": ["First Half", "Second Half"],
            "Team": ["Ghana", "Somalia"]
        },
        title=f"{selected_metric}: First Half vs Second Half"
    )

    fig_half.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    fig_half.update_layout(
        template="plotly_white",
        height=450,
        xaxis_title="Match Period",
        yaxis_title=selected_metric,
        legend_title="Team",
        uniformtext_minsize=10,
        uniformtext_mode="hide"
    )

    st.plotly_chart(
        fig_half,
        use_container_width=True
    )

# Underlying statistical breakdown
st.subheader("Half-by-Half Statistical Breakdown")

st.dataframe(
    half_data[
        [
            "metric",
            "first_half_ghana",
            "first_half_somalia",
            "second_half_ghana",
            "second_half_somalia"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# Analytical observations
st.subheader("Match Observations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Ghana**")
    st.write("• Shots increased from 8 to 15.")
    st.write("• Shots on target remained at 4.")
    st.write("• Possession decreased from 78% to 74%.")
    st.write("• Pass accuracy decreased from 91% to 87%.")

with col2:
    st.markdown("**Somalia**")
    st.write("• No shots in the first half.")
    st.write("• Three shots in the second half.")
    st.write("• Two second-half shots were on target.")
    st.write("• Tackles remained at 12 in each half.")


# ==================================================
# 7. MATCH TIMELINE
# ==================================================


# ==================================================
# 8. PLAYER INTELLIGENCE
# ==================================================

st.divider()

st.header("Player Intelligence")

st.write(
    "Individual player performance and contributions "
    "from Ghana vs Somalia."
)

# Ensure numerical columns are numeric
player_numeric_columns = [
    "FotMob rating",
    "minutes_played",
    "Goals",
    "Assists",
    "Total shots",
    "Shots on target",
    "Chances created",
    "Tackles",
    "Interceptions",
    "Clearances",
    "Duels won"
]

for column in player_numeric_columns:
    if column in players.columns:
        players[column] = pd.to_numeric(
            players[column],
            errors="coerce"
        )


# --------------------------------------------------
# 8A. TOP RATED PLAYERS
# --------------------------------------------------

st.subheader("Top Rated Players")

rated_players = players.dropna(
    subset=["FotMob rating"]
).copy()

top_players = rated_players.sort_values(
    "FotMob rating",
    ascending=False
).head(10)

fig_ratings = px.bar(
    top_players.sort_values("FotMob rating"),
    x="FotMob rating",
    y="player_name",
    color="team_name",
    orientation="h",
    text="FotMob rating",
    title="Top 10 Players by FotMob Rating",
    color_discrete_map={
        "Ghana": "#168447",
        "Somalia": "#A7DCC0"
    }
)

fig_ratings.update_layout(
    template="plotly_white",
    height=500,
    xaxis_title="FotMob Rating",
    yaxis_title="Player",
    legend_title="Team"
)

fig_ratings.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig_ratings,
    use_container_width=True
)


# --------------------------------------------------
# 8B. PLAYER SEARCH
# --------------------------------------------------

st.subheader("Explore Individual Players")

player_names = sorted(
    players["player_name"].dropna().unique()
)

selected_player = st.selectbox(
    "Select a player",
    player_names
)

player_data = players[
    players["player_name"] == selected_player
]

# TEMPORARY DATA QUALITY CHECK
if selected_player == "Mukhtar Suleiman":
    st.write("Mukhtar Suleiman source records:")
    st.dataframe(
        player_data[
            [
                "player_id",
                "player_name",
                "team_name",
                "lineup_participation_status",
                "minutes_played"
            ]
        ],
        use_container_width=True
    )

if not player_data.empty:

    player = player_data.iloc[0]

    st.markdown(f"### {player['player_name']}")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Team",
        player["team_name"]
    )

    rating = player.get("FotMob rating")

    col2.metric(
        "FotMob Rating",
        f"{rating:.2f}" if pd.notna(rating) else "N/A"
    )

    minutes = player.get("minutes_played")

    col3.metric(
        "Minutes Played",
        f"{minutes:.0f}" if pd.notna(minutes) else "N/A"
    )

    # Player performance statistics
    st.markdown("#### Performance Statistics")

    available_metrics = [
        "Goals",
        "Assists",
        "Total shots",
        "Shots on target",
        "Chances created",
        "Tackles",
        "Interceptions",
        "Clearances",
        "Duels won"
    ]

    available_metrics = [
        metric for metric in available_metrics
        if metric in players.columns
        and pd.notna(player.get(metric))
    ]

    if available_metrics:

        player_stats = pd.DataFrame({
            "Metric": available_metrics,
            "Value": [
                player[metric]
                for metric in available_metrics
            ]
        })

        st.dataframe(
            player_stats,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No individual performance metrics are "
            "available for this player."
        )


# --------------------------------------------------
# 8C. PLAYER PERFORMANCE TABLE
# --------------------------------------------------

st.subheader("Complete Player Performance Table")

team_filter = st.selectbox(
    "Filter by team",
    ["All Teams", "Ghana", "Somalia"]
)

filtered_players = players.copy()

if team_filter != "All Teams":
    filtered_players = filtered_players[
        filtered_players["team_name"] == team_filter
    ]

display_columns = [
    "player_name",
    "team_name",
    "lineup_participation_status",
    "minutes_played",
    "FotMob rating",
    "Goals",
    "Assists",
    "Total shots",
    "Chances created",
    "Tackles",
    "Interceptions",
    "Clearances"
]

display_columns = [
    column for column in display_columns
    if column in filtered_players.columns
]

st.dataframe(
    filtered_players[display_columns].sort_values(
        "FotMob rating",
        ascending=False,
        na_position="last"
    ),
    use_container_width=True,
    hide_index=True
)



# ==================================================
# MATCH EVENT TIMELINE
# ==================================================

st.divider()

st.header("Match Event Timeline")

st.write(
    "Explore the key events that shaped Ghana's 2–0 victory "
    "over Somalia."
)

# Preserve chronological order
timeline_chart = timeline.copy()

timeline_chart["event_sequence"] = pd.to_numeric(
    timeline_chart["event_sequence"],
    errors="coerce"
)

timeline_chart = timeline_chart.sort_values(
    "event_sequence"
)

# Give half-time and full-time events their own lane
timeline_chart["team_name"] = (
    timeline_chart["team_name"].fillna("Match")
)

# Interactive event timeline
fig_timeline = px.scatter(
    timeline_chart,
    x="event_sequence",
    y="event_type",
    color="event_type",
    text="display_minute",
    hover_data=[
        "team_name",
        "event_description",
        "score_after_event"
    ],
    title="Ghana vs Somalia — Match Events",
    color_discrete_map={
        "Goal": "#168447",
        "Substitution": "#2878B5",
        "Card": "#E0A126",
        "MissedPenalty": "#D9534F",
        "Half": "#777777"
    }
)

fig_timeline.update_traces(
    marker=dict(size=15),
    textposition="top center"
)

fig_timeline.update_layout(
    template="plotly_white",
    height=480,
    xaxis_title="Event Order (chronological)",
    yaxis_title="Event Type",
    showlegend=False,
    xaxis=dict(
        tickmode="array",
        tickvals=timeline_chart["event_sequence"],
        ticktext=timeline_chart["display_minute"]
    )
)

st.plotly_chart(
    fig_timeline,
    use_container_width=True
)

# Detailed event records
with st.expander("View complete match event records"):

    st.dataframe(
        timeline_chart,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# ANALYST'S MATCH REPORT
# ==================================================

st.divider()

st.header("Analyst's Match Report")

st.markdown(
    """
    ### Ghana 2–0 Somalia

    Ghana secured a 2–0 victory, controlling much of the match
    through possession, passing and attacking territory.

    However, the underlying numbers reveal a more interesting
    story than the scoreline alone.
    """
)

# ------------------------------------------
# 1. Ghana's control of the match
# ------------------------------------------

st.subheader("1. Ghana controlled possession and territory")

col1, col2, col3 = st.columns(3)

col1.metric("Ghana Possession", "76%")
col2.metric("Ghana Total Shots", "23")
col3.metric("Ghana Box Touches", "44")

st.markdown(
    """
    Ghana recorded 76% possession, attempted 23 shots and
    registered 44 opposition-box touches.

    Somalia managed just 24% possession, three shots and
    eight opposition-box touches.

    These figures demonstrate Ghana's territorial and
    attacking control throughout the match.
    """
)

# ------------------------------------------
# 2. The difference between the halves
# ------------------------------------------

st.subheader("2. Ghana increased its attacking volume after half-time")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**First half**")
    st.metric("Ghana shots", "8")
    st.metric("Ghana shots on target", "4")
    st.metric("Possession", "78%")

with col2:
    st.markdown("**Second half**")
    st.metric("Ghana shots", "15", "+7")
    st.metric("Ghana shots on target", "4", "No change")
    st.metric("Possession", "74%", "-4 percentage points")

st.markdown(
    """
    Ghana increased its shot volume from eight to 15 after
    the interval. However, shots on target remained at four.

    This suggests that the increased attacking volume did not
    translate into more shots on target. Ghana's shot accuracy
    also fell from 50% to approximately 26.7%.
    """
)

# ------------------------------------------
# 3. Somalia's defensive workload
# ------------------------------------------

st.subheader("3. Somalia spent much of the match defending")

col1, col2, col3 = st.columns(3)

col1.metric("Somalia tackles", "24")
col2.metric("Somalia clearances", "18")
col3.metric("Somalia blocks", "5")

st.markdown(
    """
    Somalia recorded more tackles, interceptions, clearances
    and blocks than Ghana.

    This is consistent with a match in which Somalia had to
    defend for extended periods while Ghana controlled possession.

    However, defensive action counts alone do not establish
    defensive effectiveness.
    """
)

# ------------------------------------------
# 4. Individual contributions
# ------------------------------------------

st.subheader("4. Players who influenced the result")

st.markdown(
    """
    - **Jonas Adjetey:** Scored Ghana's opening goal in first-half
      stoppage time and recorded a FotMob rating of 8.22.
    - **Felix Afena-Gyan:** Scored Ghana's second goal in the
      62nd minute.
    - **Mohammed Kudus:** Recorded an assist and created five
      chances, earning a rating of 8.46.
    - **Mohammed Salisu:** Recorded an assist and earned a
      rating of 8.17.
    """
)

# ------------------------------------------
# 5. Analytical perspective
# ------------------------------------------

st.subheader("5. What the data tells us")

st.markdown(
    """
    Ghana's victory was built on sustained possession and
    territorial dominance. The team generated considerably more
    attacking volume and converted two important opportunities.

    Somalia's limited attacking output meant that Ghana's
    defensive workload was relatively lower, while Somalia
    registered a much higher number of defensive actions.

    One important caution concerns shot accuracy: Somalia's
    66.7% came from just three attempts, with two on target.
    The small sample makes that percentage less meaningful
    as a measure of sustained attacking quality.

    **Final assessment:** Ghana deserved the statistical
    advantage, but the difference between shot volume and
    shots on target provides an important area for further
    attacking analysis.
    """
)

# ==================================================
# 8. DATA SOURCE
# ==================================================

st.divider()

st.caption(
    "Source: FotMob match data | "
    "Built using a Python ETL pipeline"
)
