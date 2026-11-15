
import pandas as pd

from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"


# ============================================================
# BUILD RECONCILED APPEARANCE DATASET
# ============================================================

def build_reconciled_appearances(
    processed_dir=PROCESSED_DIR
):

    processed_dir = Path(processed_dir)

    lineups_file = processed_dir / "lineups.csv"
    appearances_file = processed_dir / "player_appearances.csv"

    # --------------------------------------------------------
    # LOAD SOURCE DATASETS
    # --------------------------------------------------------

    if not lineups_file.exists():
        raise FileNotFoundError(
            f"Lineup dataset not found: {lineups_file}"
        )

    if not appearances_file.exists():
        raise FileNotFoundError(
            f"Appearance dataset not found: {appearances_file}"
        )

    lineups = pd.read_csv(lineups_file)

    appearances = pd.read_csv(appearances_file)

    # --------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------------

    lineup_required = [
        "match_id",
        "player_id",
        "player_name",
        "team_name",
        "participation_status",
        "sub_out_minute",
    ]

    appearance_required = [
        "match_id",
        "player_id",
        "player_name",
        "team_name",
        "opta_id",
        "minutes_played",
        "participation_status",
    ]

    missing_lineup = [
        col for col in lineup_required
        if col not in lineups.columns
    ]

    missing_appearance = [
        col for col in appearance_required
        if col not in appearances.columns
    ]

    if missing_lineup:
        raise ValueError(
            f"Missing lineup columns: {missing_lineup}"
        )

    if missing_appearance:
        raise ValueError(
            f"Missing appearance columns: {missing_appearance}"
        )

    # --------------------------------------------------------
    # VALIDATE PLAYER IDENTIFIERS
    # --------------------------------------------------------

    join_keys = ["match_id", "player_id"]

    if lineups[join_keys].isna().any().any():
        raise ValueError(
            "Missing match_id or player_id in lineup dataset."
        )

    if appearances[join_keys].isna().any().any():
        raise ValueError(
            "Missing match_id or player_id in appearance dataset."
        )

    lineup_duplicates = lineups.duplicated(
        subset=join_keys
    ).sum()

    appearance_duplicates = appearances.duplicated(
        subset=join_keys
    ).sum()

    print("\nSOURCE DATA QUALITY CHECK")
    print("=" * 55)

    print("Duplicate lineup records:", lineup_duplicates)
    print("Duplicate appearance records:", appearance_duplicates)

    if lineup_duplicates > 0:
        raise ValueError(
            "Duplicate match/player records found in lineups."
        )

    if appearance_duplicates > 0:
        raise ValueError(
            "Duplicate match/player records found in appearances."
        )

    # --------------------------------------------------------
    # SELECT APPEARANCE FIELDS
    # --------------------------------------------------------

    appearance_fields = appearances[
        [
            "match_id",
            "player_id",
            "opta_id",
            "minutes_played",
            "participation_status",
        ]
    ].copy()

    appearance_fields = appearance_fields.rename(
        columns={
            "participation_status": "appearance_feed_status"
        }
    )

    # --------------------------------------------------------
    # USE LINEUPS AS THE CANONICAL ROSTER
    # --------------------------------------------------------

    reconciled = lineups.merge(
        appearance_fields,
        on=join_keys,
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    # --------------------------------------------------------
    # IDENTIFY MATCHED APPEARANCE RECORDS
    # --------------------------------------------------------

    reconciled["appearance_record_found"] = (
        reconciled["_merge"] == "both"
    )

    reconciled = reconciled.drop(
        columns="_merge"
    )

    # Preserve lineup participation as the main classification
    reconciled = reconciled.rename(
        columns={
            "participation_status":
            "lineup_participation_status"
        }
    )

    # --------------------------------------------------------
    # IDENTIFY UNMATCHED APPEARANCE RECORDS
    # --------------------------------------------------------

    lineup_keys = lineups[join_keys].drop_duplicates()

    appearance_anomalies = appearances.merge(
        lineup_keys,
        on=join_keys,
        how="left",
        indicator=True,
        validate="one_to_one",
    )

    appearance_anomalies = appearance_anomalies[
        appearance_anomalies["_merge"] == "left_only"
    ].drop(
        columns="_merge"
    )

    # --------------------------------------------------------
    # SAVE OUTPUT DATASETS
    # --------------------------------------------------------

    reconciled_file = (
        processed_dir / "player_appearances_reconciled.csv"
    )

    anomalies_file = (
        processed_dir / "appearance_source_anomalies.csv"
    )

    reconciled.to_csv(
        reconciled_file,
        index=False
    )

    appearance_anomalies.to_csv(
        anomalies_file,
        index=False
    )

    # --------------------------------------------------------
    # VALIDATE OUTPUTS
    # --------------------------------------------------------

    if reconciled.duplicated(subset=join_keys).any():
        raise ValueError(
            "Duplicate records found in reconciled roster."
        )

    if len(reconciled) != len(lineups):
        raise ValueError(
            "Reconciled roster does not match lineup record count."
        )

    if (
        reconciled["appearance_record_found"].sum()
        + len(appearance_anomalies)
        != len(appearances)
    ):
        raise ValueError(
            "Appearance reconciliation record counts do not balance."
        )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print("\nRECONCILED APPEARANCE DATASET")
    print("=" * 55)

    print("Total roster records:", len(reconciled))

    print(
        "Unique players:",
        reconciled["player_id"].nunique()
    )

    print("\nLineup participation:")

    print(
        reconciled["lineup_participation_status"]
        .value_counts(dropna=False)
    )

    print("\nAppearance feed record matching:")

    print(
        reconciled["appearance_record_found"]
        .value_counts(dropna=False)
    )

    print("\nPlayers without matching appearance records:")

    print(
        reconciled.loc[
            ~reconciled["appearance_record_found"],
            [
                "player_id",
                "player_name",
                "team_name",
                "lineup_participation_status",
                "sub_out_minute",
            ]
        ].to_string(index=False)
    )

    print("\nUnmatched appearance source records:")

    print(
        appearance_anomalies[
            [
                "player_id",
                "player_name",
                "team_name",
                "minutes_played",
                "participation_status",
            ]
        ].to_string(index=False)
    )

    print("\nSaved datasets:")
    print(reconciled_file)
    print(anomalies_file)

    return reconciled, appearance_anomalies


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    build_reconciled_appearances()
