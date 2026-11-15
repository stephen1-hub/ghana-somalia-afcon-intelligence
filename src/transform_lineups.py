
import json
import pandas as pd

from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MATCH_ID = 6040239

RAW_FILE = (
    BASE_DIR / "data" / "raw"
    / f"match_details_{MATCH_ID}.json"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"


# ============================================================
# TRANSFORM LINEUP DATA
# ============================================================

def transform_lineups(
    raw_file=RAW_FILE,
    output_dir=OUTPUT_DIR
):

    raw_file = Path(raw_file)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # LOAD RAW MATCH DATA
    # --------------------------------------------------------

    with open(
        raw_file,
        "r",
        encoding="utf-8"
    ) as file:

        raw = json.load(file)

    content = raw["props"]["pageProps"]["content"]

    lineup_data = content["lineup"]

    match_id = lineup_data.get("matchId", MATCH_ID)

    # --------------------------------------------------------
    # TRANSFORM STARTING XI AND SUBSTITUTES
    # --------------------------------------------------------

    records = []

    for side in ["homeTeam", "awayTeam"]:

        team = lineup_data.get(side, {})

        team_name = team.get("name")
        formation = team.get("formation")

        player_groups = [
            ("starter", team.get("starters", [])),
            ("substitute", team.get("subs", []))
        ]

        for role, players in player_groups:

            for player in players:

                performance = player.get("performance") or {}

                substitution_events = (
                    performance.get("substitutionEvents") or []
                )

                sub_in_events = [
                    event for event in substitution_events
                    if event.get("type") == "subIn"
                ]

                sub_out_events = [
                    event for event in substitution_events
                    if event.get("type") == "subOut"
                ]

                # Determine participation
                if role == "starter":
                    participation_status = "played"

                elif sub_in_events:
                    participation_status = "played"

                else:
                    participation_status = "unused_substitute"

                horizontal = (
                    player.get("horizontalLayout") or {}
                )

                vertical = (
                    player.get("verticalLayout") or {}
                )

                records.append({

                    "match_id": match_id,
                    "team_name": team_name,
                    "formation": formation,

                    "player_id": player.get("id"),
                    "player_name": player.get("name"),
                    "first_name": player.get("firstName"),
                    "last_name": player.get("lastName"),

                    "shirt_number": player.get("shirtNumber"),
                    "age": player.get("age"),

                    "position_id": player.get("positionId"),
                    "usual_position_id": player.get(
                        "usualPlayingPositionId"
                    ),

                    "club": player.get("primaryTeamName"),

                    "role": role,
                    "participation_status": participation_status,

                    "rating": performance.get("rating"),

                    "is_player_of_match": performance.get(
                        "playerOfTheMatch"
                    ),

                    "sub_in_minute": (
                        sub_in_events[0].get("time")
                        if sub_in_events else None
                    ),

                    "sub_out_minute": (
                        sub_out_events[0].get("time")
                        if sub_out_events else None
                    ),

                    "horizontal_x": horizontal.get("x"),
                    "horizontal_y": horizontal.get("y"),

                    "vertical_x": vertical.get("x"),
                    "vertical_y": vertical.get("y")

                })

    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    lineups_df = pd.DataFrame(records)

    if lineups_df.empty:
        raise ValueError("No lineup records were extracted.")

    # --------------------------------------------------------
    # DATA QUALITY VALIDATION
    # --------------------------------------------------------

    if lineups_df["player_id"].isna().any():
        raise ValueError(
            "Lineup contains missing player IDs."
        )

    duplicate_ids = lineups_df[
        lineups_df.duplicated(
            subset=["match_id", "player_id"],
            keep=False
        )
    ]

    if not duplicate_ids.empty:
        raise ValueError(
            "Duplicate player IDs found in lineup data:\n"
            f"{duplicate_ids[['player_id', 'player_name', 'team_name']]}"
        )

    # --------------------------------------------------------
    # SAVE PROCESSED DATASET
    # --------------------------------------------------------

    output_file = output_dir / "lineups.csv"

    lineups_df.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print("\nLINEUP TRANSFORMATION COMPLETE")
    print("=" * 50)

    print("\nDataset shape:")
    print(lineups_df.shape)

    print("\nPlayers by team and role:")

    print(
        lineups_df.groupby(
            ["team_name", "role"]
        ).size()
    )

    print("\nParticipation status:")

    print(
        lineups_df.groupby(
            ["team_name", "participation_status"]
        ).size()
    )

    print("\nDuplicate player IDs:")
    print(
        lineups_df["player_id"].duplicated().sum()
    )

    print("\nMissing player IDs:")
    print(
        lineups_df["player_id"].isna().sum()
    )

    print("\nFormation by team:")

    print(
        lineups_df.groupby(
            "team_name"
        )["formation"].first()
    )

    print("\nPreview:")

    print(
        lineups_df[
            [
                "team_name",
                "player_name",
                "role",
                "participation_status",
                "rating"
            ]
        ].to_string(index=False)
    )

    print(f"\nSaved to: {output_file}")

    return lineups_df


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_lineups()
