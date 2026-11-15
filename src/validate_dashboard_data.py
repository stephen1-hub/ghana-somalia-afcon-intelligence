
import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATA_DIR = PROCESSED_DIR / "match_intelligence"

MATCH_ID = 6040239
HOME_TEAM = "Ghana"
AWAY_TEAM = "Somalia"


def check(results, name, condition, details=""):
    """Record and print an individual validation result."""

    passed = bool(condition)
    status = "PASS" if passed else "FAIL"

    results.append((name, status, details))

    symbol = "✓" if passed else "✗"
    print(f"{symbol} {status}: {name}")

    if details:
        print(f"    {details}")


def load_csv(path):
    """Load a CSV file or raise a clear error."""

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    return pd.read_csv(path)


def numeric_value(value):
    return pd.to_numeric(value, errors="coerce")


def validate_dashboard_data(
    processed_dir=PROCESSED_DIR,
    data_dir=DATA_DIR
):
    """Validate the quality and consistency of dashboard datasets."""

    processed_dir = Path(processed_dir)
    data_dir = Path(data_dir)

    results = []

    print("\n" + "=" * 55)
    print("GHANA VS SOMALIA — DASHBOARD DATA QUALITY AUDIT")
    print("=" * 55)

    # --------------------------------------------------
    # 1. LOAD DASHBOARD DATASETS
    # --------------------------------------------------

    try:
        summary_path = data_dir / "match_intelligence_summary.json"

        if not summary_path.exists():
            raise FileNotFoundError(
                f"Missing file: {summary_path}"
            )

        with open(summary_path, "r", encoding="utf-8") as file:
            summary = json.load(file)

        metrics = load_csv(
            data_dir / "match_intelligence_metrics.csv"
        )

        timeline = load_csv(
            data_dir / "match_intelligence_timeline.csv"
        )

        players = load_csv(
            data_dir / "match_intelligence_players.csv"
        )

        half_performance = load_csv(
            processed_dir / "half_performance_comparison.csv"
        )

        check(
            results,
            "All dashboard datasets loaded",
            True,
            "JSON summary and four CSV datasets loaded successfully"
        )

    except (FileNotFoundError, json.JSONDecodeError, pd.errors.ParserError) as error:
        check(
            results,
            "All dashboard datasets loaded",
            False,
            str(error)
        )

        print("\nAudit stopped: dataset loading failed.")

        return {
            "status": "failed",
            "checks_passed": 0,
            "checks_failed": 1,
            "total_checks": 1,
            "results": results
        }

    # --------------------------------------------------
    # 2. RECORD COUNTS
    # --------------------------------------------------

    expected_counts = {
        "Match metrics record count": (len(metrics), 14),
        "Match timeline record count": (len(timeline), 15),
        "Player dataset record count": (len(players), 46),
        "Half-performance record count": (len(half_performance), 9)
    }

    for name, (actual, expected) in expected_counts.items():
        check(
            results,
            name,
            actual == expected,
            f"Expected {expected}; found {actual}"
        )

    # --------------------------------------------------
    # 3. REQUIRED COLUMNS
    # --------------------------------------------------

    required_columns = {
        "metrics": {
            "Metric", HOME_TEAM, AWAY_TEAM
        },
        "timeline": {
            "event_sequence", "display_minute",
            "event_type", "event_description",
            "score_after_event"
        },
        "players": {
            "player_id", "player_name", "team_name",
            "lineup_participation_status",
            "minutes_played", "FotMob rating"
        },
        "half_performance": {
            "metric", "first_half_ghana",
            "first_half_somalia",
            "second_half_ghana",
            "second_half_somalia"
        }
    }

    datasets = {
        "metrics": metrics,
        "timeline": timeline,
        "players": players,
        "half_performance": half_performance
    }

    for dataset_name, required in required_columns.items():
        missing = required - set(datasets[dataset_name].columns)

        check(
            results,
            f"{dataset_name}: required columns",
            len(missing) == 0,
            f"Missing columns: {sorted(missing) if missing else 'None'}"
        )

    # --------------------------------------------------
    # 4. DUPLICATE RECORD CHECKS
    # --------------------------------------------------

    if "Metric" in metrics.columns:
        check(
            results,
            "No duplicate metric names",
            metrics["Metric"].is_unique,
            f"Unique metrics: {metrics['Metric'].nunique()}"
        )

    if "player_id" in players.columns:
        check(
            results,
            "No duplicate player IDs",
            players["player_id"].is_unique,
            f"Unique player IDs: {players['player_id'].nunique()}"
        )

    if "event_sequence" in timeline.columns:
        check(
            results,
            "No duplicate event sequence numbers",
            timeline["event_sequence"].is_unique,
            f"Unique event sequences: {timeline['event_sequence'].nunique()}"
        )

    # --------------------------------------------------
    # 5. MATCH INFORMATION
    # --------------------------------------------------

    match = summary.get("match_information", {})

    check(
        results,
        "Correct home team",
        match.get("home_team") == HOME_TEAM,
        f"Found: {match.get('home_team')}"
    )

    check(
        results,
        "Correct away team",
        match.get("away_team") == AWAY_TEAM,
        f"Found: {match.get('away_team')}"
    )

    check(
        results,
        "Correct match ID",
        str(match.get("match_id")) == str(MATCH_ID),
        f"Found: {match.get('match_id')}"
    )

    home_score = numeric_value(match.get("home_score"))
    away_score = numeric_value(match.get("away_score"))

    score_valid = (
        pd.notna(home_score)
        and pd.notna(away_score)
        and home_score == 2
        and away_score == 0
    )

    check(
        results,
        "Correct final score",
        score_valid,
        f"Score: {match.get('home_score')} - {match.get('away_score')}"
    )

    # --------------------------------------------------
    # 6. TEAM METRIC ACCURACY
    # --------------------------------------------------

    expected_metrics = {
        "Possession (%)": (76, 24),
        "Total shots": (23, 3),
        "Shots on target": (8, 2),
        "Opposition box touches": (44, 8),
        "Pass accuracy (%)": (89, 57),
        "Tackles": (8, 24),
        "Interceptions": (6, 8),
        "Clearances": (14, 18),
        "Blocks": (1, 5),
        "Fouls committed": (14, 11)
    }

    if {"Metric", HOME_TEAM, AWAY_TEAM}.issubset(metrics.columns):
        metrics_index = metrics.set_index("Metric")

        for metric_name, expected in expected_metrics.items():

            if metric_name not in metrics_index.index:
                check(
                    results,
                    f"Metric accuracy: {metric_name}",
                    False,
                    "Metric not found in dashboard metrics"
                )
                continue

            row = metrics_index.loc[metric_name]

            # Duplicate names are already checked above.
            if isinstance(row, pd.DataFrame):
                check(
                    results,
                    f"Metric accuracy: {metric_name}",
                    False,
                    "Multiple rows found for this metric"
                )
                continue

            actual = (
                numeric_value(row[HOME_TEAM]),
                numeric_value(row[AWAY_TEAM])
            )

            valid = (
                pd.notna(actual[0])
                and pd.notna(actual[1])
                and abs(actual[0] - expected[0]) < 0.01
                and abs(actual[1] - expected[1]) < 0.01
            )

            check(
                results,
                f"Metric accuracy: {metric_name}",
                valid,
                f"Expected {expected}; found {actual}"
            )

    # --------------------------------------------------
    # 7. EVENT TIMELINE VALIDATION
    # --------------------------------------------------

    if "event_type" in timeline.columns:
        event_counts = timeline["event_type"].value_counts().to_dict()

        expected_events = {
            "Goal": 2,
            "Substitution": 9,
            "MissedPenalty": 1,
            "Card": 1,
            "Half": 2
        }

        for event_type, expected_count in expected_events.items():
            actual_count = event_counts.get(event_type, 0)

            check(
                results,
                f"Timeline events: {event_type}",
                actual_count == expected_count,
                f"Expected {expected_count}; found {actual_count}"
            )

        check(
            results,
            "Timeline contains both goals",
            (timeline["event_type"] == "Goal").sum() == 2,
            "Expected two goals"
        )

    if "event_sequence" in timeline.columns:
        sequence = pd.to_numeric(
            timeline["event_sequence"],
            errors="coerce"
        )

        sequence_valid = (
            sequence.notna().all()
            and sequence.is_monotonic_increasing
        )

        check(
            results,
            "Timeline chronological sequence",
            sequence_valid,
            "Original event order must already be chronological"
        )

    # --------------------------------------------------
    # 8. PLAYER PARTICIPATION VALIDATION
    # --------------------------------------------------

    if "lineup_participation_status" in players.columns:

        participation_counts = (
            players["lineup_participation_status"]
            .value_counts()
            .to_dict()
        )

        check(
            results,
            "Players who participated",
            participation_counts.get("played", 0) == 31,
            f"Found: {participation_counts.get('played', 0)}"
        )

        check(
            results,
            "Unused substitutes",
            participation_counts.get("unused_substitute", 0) == 15,
            f"Found: {participation_counts.get('unused_substitute', 0)}"
        )

    if "team_name" in players.columns:
        actual_teams = set(players["team_name"].dropna().unique())

        check(
            results,
            "Only Ghana and Somalia in player dataset",
            actual_teams == {HOME_TEAM, AWAY_TEAM},
            f"Teams: {sorted(actual_teams)}"
        )

    # --------------------------------------------------
    # 9. MISSING VALUE AUDIT
    # --------------------------------------------------

    print("\nMISSING PLAYER DATA")
    print("-" * 55)

    columns_to_audit = [
        "minutes_played",
        "FotMob rating",
        "Goals",
        "Assists",
        "Total shots",
        "Shots on target",
        "Chances created",
        "Tackles",
        "Interceptions",
        "Clearances"
    ]

    for column in columns_to_audit:
        if column in players.columns:
            missing_count = players[column].isna().sum()

            print(
                f"{column:<25} "
                f"{missing_count:>3} missing values"
            )

    print(
        "\nMissing player statistics are reported, not "
        "automatically replaced with zero."
    )

    # --------------------------------------------------
    # 10. FINAL AUDIT SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 55)
    print("FINAL AUDIT SUMMARY")
    print("=" * 55)

    passed = sum(status == "PASS" for _, status, _ in results)
    failed = sum(status == "FAIL" for _, status, _ in results)

    print(f"Checks passed: {passed}")
    print(f"Checks failed: {failed}")
    print(f"Total checks:  {len(results)}")

    if failed == 0:
        print("\nALL DASHBOARD DATA QUALITY CHECKS PASSED.")
        status = "passed"
    else:
        print("\nSOME CHECKS FAILED. REVIEW THE FAILURES ABOVE.")
        status = "failed"

    print("=" * 55)

    return {
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "total_checks": len(results),
        "results": results
    }


if __name__ == "__main__":
    validate_dashboard_data()
