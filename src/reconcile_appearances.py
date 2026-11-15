
import pandas as pd

from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"


# ============================================================
# RECONCILE PLAYER APPEARANCES
# ============================================================

def reconcile_appearances(
    processed_dir=PROCESSED_DIR
):

    processed_dir = Path(processed_dir)

    appearances_file = (
        processed_dir / "player_appearances.csv"
    )

    lineups_file = (
        processed_dir / "lineups.csv"
    )

    # --------------------------------------------------------
    # LOAD DATASETS
    # --------------------------------------------------------

    if not appearances_file.exists():
        raise FileNotFoundError(
            f"Appearance dataset not found: {appearances_file}"
        )

    if not lineups_file.exists():
        raise FileNotFoundError(
            f"Lineup dataset not found: {lineups_file}"
        )

    appearances = pd.read_csv(appearances_file)

    lineups = pd.read_csv(lineups_file)

    # --------------------------------------------------------
    # VALIDATE REQUIRED COLUMNS
    # --------------------------------------------------------

    appearance_columns = [
        "match_id",
        "player_id",
        "player_name",
        "team_name",
        "minutes_played",
        "participation_status",
    ]

    lineup_columns = [
        "match_id",
        "player_id",
        "player_name",
        "team_name",
        "role",
        "participation_status",
        "sub_in_minute",
        "sub_out_minute",
    ]

    missing_appearance_columns = [
        column for column in appearance_columns
        if column not in appearances.columns
    ]

    missing_lineup_columns = [
        column for column in lineup_columns
        if column not in lineups.columns
    ]

    if missing_appearance_columns:
        raise ValueError(
            "Missing appearance columns: "
            f"{missing_appearance_columns}"
        )

    if missing_lineup_columns:
        raise ValueError(
            "Missing lineup columns: "
            f"{missing_lineup_columns}"
        )

    # --------------------------------------------------------
    # DUPLICATE CHECKS
    # --------------------------------------------------------

    print("\nDUPLICATE CHECK")
    print("=" * 50)

    appearance_duplicates = appearances.duplicated(
        subset=["match_id", "player_id"]
    ).sum()

    lineup_duplicates = lineups.duplicated(
        subset=["match_id", "player_id"]
    ).sum()

    print(
        "Duplicate appearance records:",
        appearance_duplicates
    )

    print(
        "Duplicate lineup records:",
        lineup_duplicates
    )

    if appearance_duplicates > 0:
        raise ValueError(
            "Duplicate match/player records found "
            "in player appearances."
        )

    if lineup_duplicates > 0:
        raise ValueError(
            "Duplicate match/player records found "
            "in lineups."
        )

    if appearances[
        ["match_id", "player_id"]
    ].isna().any().any():

        raise ValueError(
            "Missing match ID or player ID in appearance data."
        )

    if lineups[
        ["match_id", "player_id"]
    ].isna().any().any():

        raise ValueError(
            "Missing match ID or player ID in lineup data."
        )

    # --------------------------------------------------------
    # SELECT FIELDS FOR RECONCILIATION
    # --------------------------------------------------------

    appearance_check = appearances[
        appearance_columns
    ].copy()

    lineup_check = lineups[
        lineup_columns
    ].copy()

    # --------------------------------------------------------
    # PRESERVE SOURCE-SPECIFIC FIELDS
    # --------------------------------------------------------

    appearance_check = appearance_check.rename(
        columns={
            "player_name": "appearance_player_name",
            "team_name": "appearance_team",
            "participation_status": "appearance_status",
        }
    )

    lineup_check = lineup_check.rename(
        columns={
            "player_name": "lineup_player_name",
            "team_name": "lineup_team",
            "participation_status": "lineup_status",
        }
    )

    # --------------------------------------------------------
    # RECONCILE USING MATCH ID AND PLAYER ID
    # --------------------------------------------------------

    reconciliation = appearance_check.merge(
        lineup_check,
        on=["match_id", "player_id"],
        how="outer",
        indicator=True,
        validate="one_to_one",
    )

    # --------------------------------------------------------
    # CLASSIFY RECONCILIATION RESULTS
    # --------------------------------------------------------

    status_map = {
        "both": "matched",
        "left_only": "appearance_only",
        "right_only": "lineup_only",
    }

    reconciliation["reconciliation_status"] = (
        reconciliation["_merge"].map(status_map)
    )

    # --------------------------------------------------------
    # RETAIN AVAILABLE PLAYER AND TEAM DETAILS
    # --------------------------------------------------------

    reconciliation["player_name"] = (
        reconciliation["lineup_player_name"]
        .combine_first(
            reconciliation["appearance_player_name"]
        )
    )

    reconciliation["team_name"] = (
        reconciliation["lineup_team"]
        .combine_first(
            reconciliation["appearance_team"]
        )
    )

    # --------------------------------------------------------
    # SAVE RECONCILIATION REPORT
    # --------------------------------------------------------

    output_file = (
        processed_dir / "appearance_reconciliation.csv"
    )

    reconciliation.drop(
        columns=["_merge"]
    ).to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print("\nAPPEARANCE RECONCILIATION")
    print("=" * 50)

    print("Appearance records:", len(appearances))
    print("Lineup records:", len(lineups))
    print("Reconciliation records:", len(reconciliation))

    print("\nRECONCILIATION STATUS")

    print(
        reconciliation["reconciliation_status"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------------
    # SHOW UNMATCHED RECORDS
    # --------------------------------------------------------

    columns_to_show = [
        "player_id",
        "player_name",
        "team_name",
        "appearance_status",
        "minutes_played",
        "lineup_status",
        "role",
        "sub_in_minute",
        "sub_out_minute",
    ]

    for status in ["lineup_only", "appearance_only"]:

        print(f"\n{status.upper()} RECORDS")
        print("=" * 50)

        unmatched = reconciliation[
            reconciliation["reconciliation_status"] == status
        ]

        print(
            unmatched[columns_to_show]
            .to_string(index=False)
        )

    print("\nSaved reconciliation report:")
    print(output_file)

    return reconciliation


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    reconcile_appearances()
