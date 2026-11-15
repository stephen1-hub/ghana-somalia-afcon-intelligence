
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
# TRANSFORM PLAYER DATA
# ============================================================

def transform_player_statistics(
    raw_file=RAW_FILE,
    output_dir=OUTPUT_DIR,
    match_id=MATCH_ID
):

    raw_file = Path(raw_file)
    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # LOAD RAW DATA
    # --------------------------------------------------------

    with open(
        raw_file,
        "r",
        encoding="utf-8"
    ) as file:

        raw = json.load(file)

    content = raw["props"]["pageProps"]["content"]

    player_data = content["playerStats"]

    # --------------------------------------------------------
    # TRANSFORM PLAYER RECORDS
    # --------------------------------------------------------

    player_records = []
    stat_records = []

    for player_id, player in player_data.items():

        player_id = int(player_id)

        player_categories = player.get("stats") or []

        # Find minutes played
        minutes_played = None

        for category in player_categories:

            if category.get("title") == "Top stats":

                minutes_metric = category.get("stats", {}).get(
                    "Minutes played"
                )

                if minutes_metric:
                    minutes_played = (
                        minutes_metric.get("stat", {}).get("value")
                    )

        # Determine participation without assuming
        # missing statistics mean zero minutes
        if minutes_played is None:
            participation_status = "unknown"

        elif minutes_played > 0:
            participation_status = "played"

        else:
            participation_status = "did_not_play"

        # ----------------------------------------------------
        # PLAYER ROSTER RECORD
        # ----------------------------------------------------

        player_records.append({
            "match_id": match_id,
            "player_id": player_id,
            "opta_id": player.get("optaId"),
            "player_name": player.get("name"),
            "team_id": player.get("teamId"),
            "team_name": player.get("teamName"),
            "shirt_number": player.get("shirtNumber"),
            "position_id": player.get("positionId"),
            "usual_position": player.get("usualPosition"),
            "is_goalkeeper": player.get("isGoalkeeper"),
            "minutes_played": minutes_played,
            "participation_status": participation_status
        })

        # ----------------------------------------------------
        # PLAYER STATISTICS RECORDS
        # ----------------------------------------------------

        for category in player_categories:

            category_name = category.get("title")
            category_key = category.get("key")

            metrics = category.get("stats") or {}

            for metric_name, metric_data in metrics.items():

                stat = metric_data.get("stat") or {}

                value = stat.get("value")
                total = stat.get("total")
                value_type = stat.get("type")

                # Calculate percentage only when applicable
                percentage = None

                if (
                    value_type == "fractionWithPercentage"
                    and value is not None
                    and total is not None
                    and total > 0
                ):
                    percentage = round(
                        (value / total) * 100,
                        2
                    )

                stat_records.append({
                    "match_id": match_id,
                    "player_id": player_id,
                    "player_name": player.get("name"),
                    "team_name": player.get("teamName"),
                    "category": category_name,
                    "category_key": category_key,
                    "metric": metric_name,
                    "metric_key": metric_data.get("key"),
                    "value": value,
                    "total": total,
                    "percentage": percentage,
                    "value_type": value_type
                })

    # --------------------------------------------------------
    # CREATE DATAFRAMES
    # --------------------------------------------------------

    players_df = pd.DataFrame(player_records)

    statistics_df = pd.DataFrame(stat_records)

    if players_df.empty:
        raise ValueError("No player appearance records extracted.")

    if statistics_df.empty:
        raise ValueError("No player statistics extracted.")

    # --------------------------------------------------------
    # SAVE PROCESSED DATA
    # --------------------------------------------------------

    players_file = output_dir / "player_appearances.csv"

    statistics_file = output_dir / "player_statistics.csv"

    players_df.to_csv(
        players_file,
        index=False
    )

    statistics_df.to_csv(
        statistics_file,
        index=False
    )

    # --------------------------------------------------------
    # VALIDATION AND REPORTING
    # --------------------------------------------------------

    print("\nPLAYER TRANSFORMATION COMPLETE")
    print("=" * 60)

    print("\nPLAYER ROSTER")
    print("------------------------------")

    print("Rows:", len(players_df))

    print(
        "Unique player IDs:",
        players_df["player_id"].nunique()
    )

    print("\nParticipation status:")

    print(
        players_df["participation_status"]
        .value_counts(dropna=False)
    )

    print("\nPLAYER STATISTICS")
    print("------------------------------")

    print("Rows:", len(statistics_df))

    print(
        "Unique players:",
        statistics_df["player_id"].nunique()
    )

    print("\nCategories:")
    print(statistics_df["category"].unique())

    print("\nSample player records:")

    print(
        players_df.head(5).to_string(index=False)
    )

    print("\nSample statistical records:")

    print(
        statistics_df.head(10).to_string(index=False)
    )

    print("\nDuplicate player IDs:")

    print(
        players_df["player_id"].duplicated().sum()
    )

    print("\nMissing values in player statistics:")

    print(statistics_df.isnull().sum())

    print("\nOUTPUT FILES")
    print(players_file)
    print(statistics_file)

    return players_df, statistics_df


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_player_statistics()
