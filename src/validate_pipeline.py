
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"


FILES = {
    "Team statistics": "team_statistics.csv",
    "Player statistics": "player_statistics.csv",
    "Lineups": "lineups.csv",
    "Match events": "match_events.csv",
    "Reconciled appearances": "player_appearances_reconciled.csv",
    "Appearance anomalies": "appearance_source_anomalies.csv",
    "Reconciliation audit": "appearance_reconciliation.csv",
}


DEFAULT_EXPECTATIONS = {
    "roster_records": 46,
    "unique_player_ids": 46,
    "played": 31,
    "unused_substitutes": 15,
    "appearance_records_found": 43,
    "appearance_anomalies": 2,
    "match_events": 15,
    "team_statistics": 111,
    "player_statistics": 883,
}


def load_pipeline_datasets(data_dir=DATA_DIR):
    """Load all required processed datasets."""

    data_dir = Path(data_dir)
    datasets = {}

    for name, filename in FILES.items():
        path = data_dir / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {path}"
            )

        datasets[name] = pd.read_csv(path)

    return datasets


def check_equal(name, actual, expected):
    """Raise an informative error when a validation fails."""

    if actual != expected:
        raise ValueError(
            f"{name} failed: expected {expected}, got {actual}"
        )

    print(f"PASS: {name} ({actual})")


def validate_pipeline(
    data_dir=DATA_DIR,
    expectations=None
):
    """Load datasets and validate the core ETL pipeline outputs.

    Pass a custom expectations dictionary to validate another match.
    """

    expected = DEFAULT_EXPECTATIONS.copy()

    if expectations is not None:
        expected.update(expectations)

    print("\nETL PIPELINE VALIDATION")
    print("=" * 65)

    datasets = load_pipeline_datasets(data_dir)

    # --------------------------------------------------------
    # DATASET INVENTORY
    # --------------------------------------------------------

    for name, df in datasets.items():
        print(f"\n{name}")
        print("Rows:", len(df))
        print("Columns:", len(df.columns))
        print("Duplicate rows:", df.duplicated().sum())

    # --------------------------------------------------------
    # CANONICAL ROSTER VALIDATION
    # --------------------------------------------------------

    roster = datasets["Reconciled appearances"]

    required_roster_columns = {
        "player_id",
        "lineup_participation_status",
        "appearance_record_found",
    }

    missing_columns = required_roster_columns - set(roster.columns)

    if missing_columns:
        raise ValueError(
            f"Reconciled appearances is missing columns: "
            f"{missing_columns}"
        )

    check_equal(
        "Roster record count",
        len(roster),
        expected["roster_records"]
    )

    check_equal(
        "Unique player IDs",
        roster["player_id"].nunique(),
        expected["unique_player_ids"]
    )

    participation = (
        roster["lineup_participation_status"]
        .value_counts()
    )

    check_equal(
        "Players classified as played",
        participation.get("played", 0),
        expected["played"]
    )

    check_equal(
        "Unused substitutes",
        participation.get("unused_substitute", 0),
        expected["unused_substitutes"]
    )

    check_equal(
        "Appearance records found",
        int(roster["appearance_record_found"].sum()),
        expected["appearance_records_found"]
    )

    # --------------------------------------------------------
    # SOURCE ANOMALY VALIDATION
    # --------------------------------------------------------

    anomalies = datasets["Appearance anomalies"]

    check_equal(
        "Preserved appearance anomalies",
        len(anomalies),
        expected["appearance_anomalies"]
    )

    # --------------------------------------------------------
    # MATCH EVENT VALIDATION
    # --------------------------------------------------------

    events = datasets["Match events"]

    check_equal(
        "Match event count",
        len(events),
        expected["match_events"]
    )

    # --------------------------------------------------------
    # TEAM STATISTICS VALIDATION
    # --------------------------------------------------------

    team_stats = datasets["Team statistics"]

    check_equal(
        "Team statistics record count",
        len(team_stats),
        expected["team_statistics"]
    )

    # --------------------------------------------------------
    # PLAYER STATISTICS VALIDATION
    # --------------------------------------------------------

    player_stats = datasets["Player statistics"]

    check_equal(
        "Player statistics record count",
        len(player_stats),
        expected["player_statistics"]
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("ALL CORE VALIDATION CHECKS PASSED")

    return {
        "status": "passed",
        "datasets_loaded": len(datasets),
        "checks_passed": len(expected),
        "dataset_rows": {
            name: len(df)
            for name, df in datasets.items()
        },
    }


if __name__ == "__main__":
    validate_pipeline()
