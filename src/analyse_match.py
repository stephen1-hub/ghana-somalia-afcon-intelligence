
from pathlib import Path
import re

import pandas as pd


# ==========================================================
# PROJECT CONFIGURATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"

MATCH_ID = 6040239
HOME_TEAM = "Ghana"
AWAY_TEAM = "Somalia"


# ==========================================================
# DATA LOADING
# ==========================================================

def load_analysis_data(data_dir=DATA_DIR):
    """Load the processed datasets required for match analysis."""

    data_dir = Path(data_dir)

    required_files = {
        "team_stats": "team_statistics.csv",
        "player_stats": "player_statistics.csv",
        "events": "match_events.csv",
        "appearances": "player_appearances_reconciled.csv",
    }

    datasets = {}

    for dataset_name, filename in required_files.items():
        file_path = data_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {file_path}"
            )

        datasets[dataset_name] = pd.read_csv(file_path)

    print("MATCH ANALYSIS DATA LOADED")
    print("=" * 50)

    for name, dataframe in datasets.items():
        print(
            f"{name}: {len(dataframe)} rows, "
            f"{len(dataframe.columns)} columns"
        )

    return datasets


# ==========================================================
# REUSABLE ANALYSIS HELPERS
# ==========================================================

def get_metric(team_stats, period, category, metric):
    """Retrieve a specific home and away team metric."""

    result = team_stats[
        (team_stats["period"] == period)
        & (team_stats["category"] == category)
        & (team_stats["metric"] == metric)
    ]

    if result.empty:
        return None, None

    row = result.iloc[0]

    return row["home_value"], row["away_value"]


def extract_number(value):
    """Extract the leading numeric value from a metric."""

    if pd.isna(value):
        return None

    match = re.search(r"-?\d+(?:\.\d+)?", str(value))

    return float(match.group()) if match else None


def extract_percentage(value):
    """Extract a percentage when one is available."""

    if pd.isna(value):
        return None

    match = re.search(r"\((\d+(?:\.\d+)?)%\)", str(value))

    return float(match.group(1)) if match else None


def safe_percentage(numerator, denominator):
    """Calculate a percentage safely."""

    if numerator is None or denominator is None:
        return None

    if pd.isna(numerator) or pd.isna(denominator):
        return None

    if denominator == 0:
        return None

    return round((numerator / denominator) * 100, 1)


# ==========================================================
# MAIN ANALYSIS ENTRY POINT
# ==========================================================

def run_match_analysis(data_dir=DATA_DIR):

    datasets = load_analysis_data(data_dir)

    team_stats = datasets["team_stats"]
    player_stats = datasets["player_stats"]
    events = datasets["events"]
    appearances = datasets["appearances"]

    print("\nAnalysis datasets are ready.")
    print(f"Match ID: {MATCH_ID}")
    print(f"Fixture: {HOME_TEAM} vs {AWAY_TEAM}")

    
    # ======================================================
    # TEAM PERFORMANCE ANALYSIS
    # ======================================================

    print("\nGHANA VS SOMALIA: TEAM PERFORMANCE")
    print("=" * 60)

    # Retrieve full-match metrics
    possession = get_metric(
        team_stats, "All", "Top stats", "Ball possession"
    )
    shots = get_metric(
        team_stats, "All", "Shots", "Total shots"
    )
    shots_on_target = get_metric(
        team_stats, "All", "Shots", "Shots on target"
    )
    shots_inside_box = get_metric(
        team_stats, "All", "Shots", "Shots inside box"
    )
    box_touches = get_metric(
        team_stats, "All", "Top stats",
        "Touches in opposition box"
    )
    accurate_passes = get_metric(
        team_stats, "All", "Top stats", "Accurate passes"
    )
    tackles = get_metric(
        team_stats, "All", "Defence", "Tackles"
    )
    interceptions = get_metric(
        team_stats, "All", "Defence", "Interceptions"
    )
    clearances = get_metric(
        team_stats, "All", "Defence", "Clearances"
    )
    big_chances = get_metric(
        team_stats, "All", "Top stats", "Big chances"
    )
    big_chances_missed = get_metric(
        team_stats, "All", "Top stats", "Big chances missed"
    )

    # Extract shooting values
    home_shots = extract_number(shots[0])
    away_shots = extract_number(shots[1])

    home_sot = extract_number(shots_on_target[0])
    away_sot = extract_number(shots_on_target[1])

    # Calculate shooting accuracy
    home_shot_accuracy = safe_percentage(
        home_sot, home_shots
    )
    away_shot_accuracy = safe_percentage(
        away_sot, away_shots
    )

    # Extract passing accuracy
    home_pass_accuracy = extract_percentage(
        accurate_passes[0]
    )
    away_pass_accuracy = extract_percentage(
        accurate_passes[1]
    )

    # Build comparison dataset
    analysis_rows = [
        {
            "metric": "Possession (%)",
            HOME_TEAM: extract_number(possession[0]),
            AWAY_TEAM: extract_number(possession[1]),
        },
        {
            "metric": "Total shots",
            HOME_TEAM: home_shots,
            AWAY_TEAM: away_shots,
        },
        {
            "metric": "Shots on target",
            HOME_TEAM: home_sot,
            AWAY_TEAM: away_sot,
        },
        {
            "metric": "Shot accuracy (%)",
            HOME_TEAM: home_shot_accuracy,
            AWAY_TEAM: away_shot_accuracy,
        },
        {
            "metric": "Shots inside box",
            HOME_TEAM: extract_number(shots_inside_box[0]),
            AWAY_TEAM: extract_number(shots_inside_box[1]),
        },
        {
            "metric": "Opposition box touches",
            HOME_TEAM: extract_number(box_touches[0]),
            AWAY_TEAM: extract_number(box_touches[1]),
        },
        {
            "metric": "Pass accuracy (%)",
            HOME_TEAM: home_pass_accuracy,
            AWAY_TEAM: away_pass_accuracy,
        },
        {
            "metric": "Tackles",
            HOME_TEAM: extract_number(tackles[0]),
            AWAY_TEAM: extract_number(tackles[1]),
        },
        {
            "metric": "Interceptions",
            HOME_TEAM: extract_number(interceptions[0]),
            AWAY_TEAM: extract_number(interceptions[1]),
        },
        {
            "metric": "Clearances",
            HOME_TEAM: extract_number(clearances[0]),
            AWAY_TEAM: extract_number(clearances[1]),
        },
        {
            "metric": "Big chances",
            HOME_TEAM: extract_number(big_chances[0]),
            AWAY_TEAM: extract_number(big_chances[1]),
        },
        {
            "metric": "Big chances missed",
            HOME_TEAM: extract_number(big_chances_missed[0]),
            AWAY_TEAM: extract_number(big_chances_missed[1]),
        },
    ]

    comparison = pd.DataFrame(analysis_rows)

    print(comparison.to_string(index=False))

    # Calculate shot conversion using match goals
    home_goals = 2
    away_goals = 0

    print("\nSHOOTING CONVERSION")
    print("-" * 40)

    print(
        f"{HOME_TEAM}: "
        f"{safe_percentage(home_goals, home_shots)}%"
    )
    print(
        f"{AWAY_TEAM}: "
        f"{safe_percentage(away_goals, away_shots)}%"
    )

    # Export
    output_file = (
        Path(data_dir) / "match_performance_comparison.csv"
    )

    comparison.to_csv(output_file, index=False)

    print("\nSaved:", output_file)


    # ======================================================
    # FIRST-HALF VS SECOND-HALF ANALYSIS
    # ======================================================

    print("\nFIRST-HALF VS SECOND-HALF PERFORMANCE")
    print("=" * 60)

    period_metrics = [
        ("Top stats", "Ball possession"),
        ("Shots", "Total shots"),
        ("Shots", "Shots on target"),
        ("Shots", "Shots inside box"),
        ("Passes", "Passes"),
        ("Passes", "Accurate passes"),
        ("Defence", "Tackles"),
        ("Defence", "Interceptions"),
        ("Defence", "Clearances"),
    ]

    half_comparison = []

    for category, metric in period_metrics:

        first_half = team_stats[
            (team_stats["period"] == "FirstHalf")
            & (team_stats["category"] == category)
            & (team_stats["metric"] == metric)
        ]

        second_half = team_stats[
            (team_stats["period"] == "SecondHalf")
            & (team_stats["category"] == category)
            & (team_stats["metric"] == metric)
        ]

        if first_half.empty or second_half.empty:
            print(f"Skipping unavailable metric: {metric}")
            continue

        half_comparison.append({
            "category": category,
            "metric": metric,
            "first_half_ghana": first_half.iloc[0]["home_value"],
            "first_half_somalia": first_half.iloc[0]["away_value"],
            "second_half_ghana": second_half.iloc[0]["home_value"],
            "second_half_somalia": second_half.iloc[0]["away_value"],
        })

    half_df = pd.DataFrame(half_comparison)

    print(half_df.to_string(index=False))

    half_output = (
        Path(data_dir) / "half_performance_comparison.csv"
    )

    half_df.to_csv(half_output, index=False)

    print("\nSaved:", half_output)


    # ======================================================
    # PLAYER PERFORMANCE ANALYSIS
    # ======================================================

    print("\nPLAYER PERFORMANCE ANALYSIS")
    print("=" * 60)

    player_performance = appearances[
        [
            "match_id",
            "player_id",
            "player_name",
            "team_name",
            "lineup_participation_status",
            "minutes_played",
        ]
    ].copy()

    metric_categories = {
        "Goals": "Top stats",
        "Assists": "Top stats",
        "FotMob rating": "Top stats",
        "Minutes played": "Top stats",
        "Total shots": "Top stats",
        "Shots on target": "Top stats",
        "Chances created": "Top stats",
        "Big chances created": "Top stats",
        "Tackles": "Defense",
        "Interceptions": "Defense",
        "Clearances": "Defense",
        "Blocks": "Defense",
        "Recoveries": "Top stats",
        "Duels won": "Duels",
        "Ground duels won": "Duels",
        "Aerial duels won": "Duels",
        "Successful dribbles": "Attack",
        "Passes into final third": "Attack",
    }

    for metric, category in metric_categories.items():

        metric_data = player_stats[
            (player_stats["metric"] == metric)
            & (player_stats["category"] == category)
        ][
            ["player_id", "team_name", "value"]
        ].copy()

        if metric_data.empty:
            print(f"Metric unavailable: {metric}")
            continue

        if metric_data.duplicated(
            subset=["player_id", "team_name"]
        ).any():
            raise ValueError(
                f"Duplicate records found for metric: {metric}"
            )

        metric_data = metric_data.rename(
            columns={"value": metric}
        )

        player_performance = player_performance.merge(
            metric_data,
            on=["player_id", "team_name"],
            how="left",
            validate="one_to_one",
        )


    # Calculate shot accuracy without replacing missing values.
    if {
        "Shots on target",
        "Total shots",
    }.issubset(player_performance.columns):

        player_performance["shot_accuracy_pct"] = (
            player_performance["Shots on target"]
            .div(player_performance["Total shots"])
            .mul(100)
            .where(player_performance["Total shots"] > 0)
        )

    # Audit FotMob minutes against reconciled lineup minutes.
    if "Minutes played" in player_performance.columns:

        playing_time_audit = player_performance[
            [
                "player_name",
                "team_name",
                "minutes_played",
                "Minutes played",
            ]
        ].copy()

        audit_file = (
            Path(data_dir) / "playing_time_audit.csv"
        )

        playing_time_audit.to_csv(
            audit_file,
            index=False,
        )

        print("\nSaved playing-time audit:", audit_file)

        player_performance = player_performance.drop(
            columns=["Minutes played"]
        )

    player_performance = player_performance.sort_values(
        ["team_name", "FotMob rating"],
        ascending=[True, False],
        na_position="last",
    )

    player_output = (
        Path(data_dir) / "player_performance_analysis.csv"
    )

    player_performance.to_csv(
        player_output,
        index=False,
    )

    print("\nTop-rated players:")
    print(
        player_performance[
            [
                "player_name",
                "team_name",
                "minutes_played",
                "FotMob rating",
            ]
        ].head(10).to_string(index=False)
    )

    print("\nPlayer dataset shape:", player_performance.shape)
    print("Saved:", player_output)

    # ======================================================
    # ATTACKING PERFORMANCE ANALYSIS
    # ======================================================

    print("\nATTACKING PERFORMANCE ANALYSIS")
    print("=" * 60)

    attacking_metrics = [
        "Goals",
        "Assists",
        "Total shots",
        "Shots on target",
        "shot_accuracy_pct",
        "Chances created",
        "Successful dribbles",
        "Passes into final third",
    ]

    available_attacking_metrics = [
        metric
        for metric in attacking_metrics
        if metric in player_performance.columns
    ]

    attacking_performance = player_performance[
        player_performance["lineup_participation_status"] == "played"
    ][
        [
            "player_id",
            "player_name",
            "team_name",
            "minutes_played",
            *available_attacking_metrics,
        ]
    ].copy()

    attacking_performance = attacking_performance.sort_values(
        ["team_name", "Goals", "Assists"],
        ascending=[True, False, False],
        na_position="last",
    )

    attacking_output = (
        Path(data_dir) / "attacking_performance_analysis.csv"
    )

    attacking_performance.to_csv(
        attacking_output,
        index=False,
    )

    print("\nTop attacking contributors:")
    print(
        attacking_performance[
            [
                "player_name",
                "team_name",
                "minutes_played",
                "Goals",
                "Assists",
                "Total shots",
                "Chances created",
            ]
        ].head(15).to_string(index=False)
    )

    print("\nAttacking dataset shape:", attacking_performance.shape)
    print("Saved:", attacking_output)

    # ======================================================
    # ATTACKING EFFICIENCY PER 90 MINUTES
    # ======================================================

    print("\nATTACKING EFFICIENCY PER 90 MINUTES")
    print("=" * 60)

    per90_data = attacking_performance[
        attacking_performance["minutes_played"] > 0
    ].copy()

    per90_metrics = [
        "Goals",
        "Assists",
        "Total shots",
        "Chances created",
    ]

    for metric in per90_metrics:
        if metric in per90_data.columns:
            per90_data[f"{metric}_per90"] = (
                per90_data[metric]
                .div(per90_data["minutes_played"])
                .mul(90)
            )

    # Goal contributions = goals + assists.
    per90_data["Goal contributions"] = (
        per90_data["Goals"] + per90_data["Assists"]
    )

    per90_data["Goal contributions_per90"] = (
        per90_data["Goal contributions"]
        .div(per90_data["minutes_played"])
        .mul(90)
    )

    per90_output = (
        Path(data_dir) / "attacking_efficiency_per90.csv"
    )

    per90_data.to_csv(per90_output, index=False)

    print("\nTop goal contributions per 90:")
    print(
        per90_data.sort_values(
            "Goal contributions_per90",
            ascending=False,
            na_position="last",
        )[
            [
                "player_name",
                "team_name",
                "minutes_played",
                "Goal contributions",
                "Goal contributions_per90",
            ]
        ].head(10).to_string(index=False)
    )

    # Apply a 30-minute minimum for a more cautious comparison.
    per90_30 = per90_data[
        per90_data["minutes_played"] >= 30
    ].copy()

    per90_30_output = (
        Path(data_dir) / "attacking_efficiency_per90_30min.csv"
    )

    per90_30.to_csv(per90_30_output, index=False)

    print("\nPlayers with at least 30 minutes:", len(per90_30))
    print("Saved:", per90_output)
    print("Saved:", per90_30_output)

        # ======================================================
    # DEFENSIVE PERFORMANCE ANALYSIS
    # ======================================================

    print("\nDEFENSIVE PERFORMANCE ANALYSIS")
    print("=" * 60)

    defensive_metrics = [
        "Tackles",
        "Interceptions",
        "Clearances",
        "Blocks",
        "Recoveries",
        "Duels won",
        "Ground duels won",
        "Aerial duels won",
    ]

    available_defensive_metrics = [
        metric
        for metric in defensive_metrics
        if metric in player_performance.columns
    ]

    defensive_performance = player_performance[
        player_performance["lineup_participation_status"] == "played"
    ][
        [
            "player_id",
            "player_name",
            "team_name",
            "minutes_played",
            *available_defensive_metrics,
        ]
    ].copy()

    defensive_output = (
        Path(data_dir) / "defensive_performance_analysis.csv"
    )

    defensive_performance.to_csv(
        defensive_output,
        index=False,
    )

    print("\nTop defensive contributors by tackles:")
    print(
        defensive_performance.sort_values(
            "Tackles",
            ascending=False,
            na_position="last",
        )[
            [
                "player_name",
                "team_name",
                "minutes_played",
                "Tackles",
                "Interceptions",
                "Clearances",
                "Blocks",
                "Duels won",
            ]
        ].head(15).to_string(index=False)
    )

    print("\nDefensive dataset shape:", defensive_performance.shape)
    print("Saved:", defensive_output)


    # ======================================================
    # DEFENSIVE EFFICIENCY PER 90 MINUTES
    # ======================================================

    print("\nDEFENSIVE EFFICIENCY PER 90 MINUTES")
    print("=" * 60)

    defensive_per90 = defensive_performance[
        defensive_performance["minutes_played"] >= 30
    ].copy()

    defensive_rate_metrics = [
        "Tackles",
        "Interceptions",
        "Clearances",
        "Blocks",
        "Duels won",
        "Ground duels won",
        "Aerial duels won",
    ]

    for metric in defensive_rate_metrics:

        if metric in defensive_per90.columns:

            defensive_per90[f"{metric}_per90"] = (
                defensive_per90[metric]
                .div(defensive_per90["minutes_played"])
                .mul(90)
            )

    defensive_per90_output = (
        Path(data_dir)
        / "defensive_efficiency_per90_30min.csv"
    )

    defensive_per90.to_csv(
        defensive_per90_output,
        index=False,
    )

    print("\nTop defensive performers by tackles per 90:")
    print(
        defensive_per90.sort_values(
            "Tackles_per90",
            ascending=False,
            na_position="last",
        )[
            [
                "player_name",
                "team_name",
                "minutes_played",
                "Tackles_per90",
                "Interceptions_per90",
                "Clearances_per90",
                "Duels won_per90",
            ]
        ].head(15).to_string(index=False)
    )

    print("\nPlayers included:", len(defensive_per90))
    print("Saved:", defensive_per90_output)


        # ======================================================
    # TEAM DEFENSIVE COMPARISON
    # ======================================================

    print("\nTEAM DEFENSIVE COMPARISON")
    print("=" * 60)

    defensive_team_metrics = [
        ("Defence", "Tackles"),
        ("Defence", "Interceptions"),
        ("Defence", "Clearances"),
        ("Defence", "Blocks"),
        ("Discipline", "Fouls committed"),
    ]

    defensive_team_rows = []

    for category, metric in defensive_team_metrics:

        row = team_stats[
            (team_stats["period"] == "All")
            & (team_stats["category"] == category)
            & (team_stats["metric"] == metric)
        ]

        if row.empty:
            print(f"Metric unavailable: {metric}")
            continue

        defensive_team_rows.append({
            "metric": metric,
            HOME_TEAM: row.iloc[0]["home_value"],
            AWAY_TEAM: row.iloc[0]["away_value"],
        })

    team_defensive_comparison = pd.DataFrame(
        defensive_team_rows
    )

    defensive_team_output = (
        Path(data_dir) / "team_defensive_comparison.csv"
    )

    team_defensive_comparison.to_csv(
        defensive_team_output,
        index=False,
    )

    print(team_defensive_comparison.to_string(index=False))
    print("\nSaved:", defensive_team_output)

        # ======================================================
    # MATCH OVERVIEW
    # ======================================================

    print("\nMATCH OVERVIEW")
    print("=" * 60)

    match_overview = pd.DataFrame([{
        "match_id": MATCH_ID,
        "competition": "Africa Cup of Nations Qualification Grp. C",
        "home_team": HOME_TEAM,
        "away_team": AWAY_TEAM,
        "home_score": 2,
        "away_score": 0,
        "result": "Ghana win",
        "match_date": "2026-11-12",
        "status": "Finished",
    }])

    overview_output = (
        Path(data_dir) / "match_overview.csv"
    )

    match_overview.to_csv(
        overview_output,
        index=False,
    )

    print(match_overview.to_string(index=False))
    print("\nSaved:", overview_output)

        # ======================================================
    # CONSOLIDATED TEAM MATCH SUMMARY
    # ======================================================

    print("\nCONSOLIDATED TEAM MATCH SUMMARY")
    print("=" * 60)

    general_summary = comparison.rename(
        columns={"metric": "Metric"}
    ).copy()

    defensive_summary = team_defensive_comparison.rename(
        columns={"metric": "Metric"}
    ).copy()

    team_match_summary = pd.concat(
        [general_summary, defensive_summary],
        ignore_index=True,
    )

    # Remove duplicate metric names while preserving the first occurrence.
    team_match_summary = team_match_summary.drop_duplicates(
        subset=["Metric"],
        keep="first",
    )

    summary_output = (
        Path(data_dir) / "team_match_summary.csv"
    )

    team_match_summary.to_csv(
        summary_output,
        index=False,
    )

    print(team_match_summary.to_string(index=False))
    print("\nSummary shape:", team_match_summary.shape)
    print("Saved:", summary_output)

    return datasets


if __name__ == "__main__":
    run_match_analysis()
