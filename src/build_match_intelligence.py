
import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = DATA_DIR / "match_intelligence"

MATCH_ID = 6040239


def load_intelligence_datasets(data_dir):
    """Load the processed datasets required for match intelligence."""

    filenames = {
        "match_overview": "match_overview.csv",
        "team_metrics": "team_match_summary.csv",
        "half_performance": "half_performance_comparison.csv",
        "player_performance": "player_performance_analysis.csv",
        "attacking_performance": "attacking_performance_analysis.csv",
        "defensive_performance": "defensive_performance_analysis.csv",
        "match_timeline": "match_timeline.csv",
    }

    datasets = {}

    for name, filename in filenames.items():
        file_path = data_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {file_path}"
            )

        datasets[name] = pd.read_csv(file_path)

    return datasets


def get_team_metric(team_metrics, metric_name, home_team, away_team):
    """Retrieve a metric for the two teams."""

    required_columns = {"Metric", home_team, away_team}

    missing_columns = required_columns - set(team_metrics.columns)

    if missing_columns:
        raise ValueError(
            f"Missing columns in team metrics: {missing_columns}"
        )

    result = team_metrics[
        team_metrics["Metric"].astype(str).str.casefold()
        == metric_name.casefold()
    ]

    if result.empty:
        return None, None

    row = result.iloc[0]

    return row[home_team], row[away_team]


def make_json_safe(value):
    """Convert pandas and NumPy values into valid JSON values."""

    if isinstance(value, dict):
        return {
            key: make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [make_json_safe(item) for item in value]

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def build_match_intelligence(
    data_dir=DATA_DIR,
    output_dir=OUTPUT_DIR
):
    """Build, export and validate the match intelligence datasets."""

    data_dir = Path(data_dir)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\nLOADING MATCH INTELLIGENCE DATASETS")
    print("=" * 65)

    datasets = load_intelligence_datasets(data_dir)

    match_overview = datasets["match_overview"]
    team_metrics = datasets["team_metrics"]
    half_performance = datasets["half_performance"]
    player_performance = datasets["player_performance"]
    attacking_performance = datasets["attacking_performance"]
    defensive_performance = datasets["defensive_performance"]
    match_timeline = datasets["match_timeline"]

    for name, dataframe in datasets.items():
        print(
            f"{name}: "
            f"{dataframe.shape[0]} rows, "
            f"{dataframe.shape[1]} columns"
        )

    # --------------------------------------------------------
    # MATCH VALIDATION
    # --------------------------------------------------------

    if len(match_overview) != 1:
        raise ValueError(
            "Expected exactly one match overview record."
        )

    match = match_overview.iloc[0]

    if int(match["match_id"]) != MATCH_ID:
        raise ValueError(
            f"Unexpected match ID: {match['match_id']}"
        )

    home_team = match["home_team"]
    away_team = match["away_team"]

    print("\nMatch ID validation: PASSED")
    print("Match:", home_team, "vs", away_team)

    # --------------------------------------------------------
    # TEAM METRIC EXTRACTION
    # --------------------------------------------------------

    print("\nBUILDING MATCH INTELLIGENCE SUMMARY")
    print("=" * 65)

    metric_names = {
        "possession": "Possession (%)",
        "total_shots": "Total shots",
        "shots_on_target": "Shots on target",
        "opposition_box_touches": "Opposition box touches",
        "pass_accuracy": "Pass accuracy (%)",
        "tackles": "Tackles",
        "interceptions": "Interceptions",
        "clearances": "Clearances",
    }

    extracted_metrics = {}

    for key, metric_name in metric_names.items():
        home_value, away_value = get_team_metric(
            team_metrics,
            metric_name,
            home_team,
            away_team
        )

        extracted_metrics[key] = {
            home_team: home_value,
            away_team: away_value
        }

    # --------------------------------------------------------
    # STRUCTURED MATCH SUMMARY
    # --------------------------------------------------------

    match_summary = {
        "match_information": {
            "match_id": int(match["match_id"]),
            "competition": match["competition"],
            "date": match["match_date"],
            "home_team": home_team,
            "away_team": away_team,
            "home_score": int(match["home_score"]),
            "away_score": int(match["away_score"]),
            "result": match["result"],
            "status": match["status"]
        },

        "team_performance": {
            key: extracted_metrics[key]
            for key in [
                "possession",
                "total_shots",
                "shots_on_target",
                "opposition_box_touches",
                "pass_accuracy"
            ]
        },

        "defensive_performance": {
            key: extracted_metrics[key]
            for key in [
                "tackles",
                "interceptions",
                "clearances"
            ]
        },

        "data_inventory": {
            "team_metrics": len(team_metrics),
            "half_performance_records": len(half_performance),
            "player_records": len(player_performance),
            "attacking_records": len(attacking_performance),
            "defensive_records": len(defensive_performance),
            "timeline_events": len(match_timeline)
        }
    }

    match_summary = make_json_safe(match_summary)

    # --------------------------------------------------------
    # EXPORT JSON SUMMARY
    # --------------------------------------------------------

    summary_output = (
        output_dir / "match_intelligence_summary.json"
    )

    with open(summary_output, "w", encoding="utf-8") as file:
        json.dump(
            match_summary,
            file,
            indent=4,
            ensure_ascii=False,
            allow_nan=False
        )

    print("\nMATCH INTELLIGENCE SUMMARY")
    print(
        json.dumps(
            match_summary,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\nSaved:", summary_output)

    # --------------------------------------------------------
    # EXPORT CONSOLIDATED DATASETS
    # --------------------------------------------------------

    print("\nEXPORTING MATCH INTELLIGENCE DATASETS")
    print("=" * 65)

    exports = {
        "match_intelligence_metrics.csv": team_metrics,
        "match_intelligence_timeline.csv": match_timeline,
        "match_intelligence_players.csv": player_performance
    }

    for filename, dataframe in exports.items():
        output_path = output_dir / filename

        dataframe.to_csv(
            output_path,
            index=False
        )

        print(
            f"{filename}: "
            f"{len(dataframe)} records exported"
        )

    # --------------------------------------------------------
    # FINAL VALIDATION
    # --------------------------------------------------------

    print("\nFINAL MATCH INTELLIGENCE VALIDATION")
    print("=" * 65)

    with open(
        summary_output,
        "r",
        encoding="utf-8"
    ) as file:
        validated_summary = json.load(file)

    if validated_summary["match_information"]["match_id"] != MATCH_ID:
        raise ValueError("Exported JSON has an unexpected match ID.")

    expected_records = {
        "match_intelligence_metrics.csv": len(team_metrics),
        "match_intelligence_timeline.csv": len(match_timeline),
        "match_intelligence_players.csv": len(player_performance)
    }

    for filename, expected_count in expected_records.items():
        file_path = output_dir / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing export: {filename}"
            )

        exported_df = pd.read_csv(file_path)

        if len(exported_df) != expected_count:
            raise ValueError(
                f"Unexpected record count in {filename}: "
                f"{len(exported_df)} instead of {expected_count}"
            )

        print(
            f"PASS: {filename} - "
            f"{len(exported_df)} records"
        )

    # Timeline sequence validation
    timeline_check = pd.read_csv(
        output_dir / "match_intelligence_timeline.csv"
    )

    if not timeline_check["event_sequence"].is_monotonic_increasing:
        raise ValueError("Timeline event sequence is not ordered.")

    if timeline_check["event_sequence"].duplicated().any():
        raise ValueError("Duplicate timeline event sequences found.")

    # Player identity validation
    players_check = pd.read_csv(
        output_dir / "match_intelligence_players.csv"
    )

    if "player_id" not in players_check.columns:
        raise ValueError("Player export has no player_id column.")

    if players_check["player_id"].isna().any():
        raise ValueError("Player export contains missing player IDs.")

    if players_check["player_id"].duplicated().any():
        raise ValueError("Duplicate player IDs found in player export.")

    print("\nPASS: Match ID validation")
    print("PASS: Event sequence validation")
    print("PASS: Player identity validation")
    print("\nALL MATCH INTELLIGENCE CHECKS PASSED")

    return match_summary


if __name__ == "__main__":
    build_match_intelligence()
