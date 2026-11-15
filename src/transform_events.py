
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
# TRANSFORM MATCH EVENTS
# ============================================================

def transform_match_events(
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

    events = content["matchFacts"]["events"]["events"]

    # --------------------------------------------------------
    # TRANSFORM EVENTS
    # --------------------------------------------------------

    records = []

    for index, event in enumerate(events, start=1):

        player = event.get("player") or {}

        is_home = event.get("isHome")

        if is_home is True:
            team_name = "Ghana"

        elif is_home is False:
            team_name = "Somalia"

        else:
            team_name = None

        # Extract substitution information
        swaps = event.get("swap") or []

        incoming_player = (
            swaps[0] if len(swaps) > 0 else {}
        )

        outgoing_player = (
            swaps[1] if len(swaps) > 1 else {}
        )

        # Extract goal score after the event
        new_score = event.get("newScore")

        if new_score is not None and len(new_score) == 2:

            home_score_after = new_score[0]
            away_score_after = new_score[1]

        else:

            home_score_after = event.get("homeScore")
            away_score_after = event.get("awayScore")

        # Store event details
        records.append({

            "match_id": match_id,
            "event_sequence": index,
            "event_id": event.get("eventId"),

            "event_type": event.get("type"),
            "event_minute": event.get("time"),
            "added_time": event.get("overloadTime"),
            "display_minute": event.get("timeStr"),

            "team_name": team_name,
            "is_home": is_home,

            "player_id": player.get("id"),
            "player_name": player.get("name"),

            "incoming_player_id": incoming_player.get("id"),
            "incoming_player": incoming_player.get("name"),

            "outgoing_player_id": outgoing_player.get("id"),
            "outgoing_player": outgoing_player.get("name"),

            "card_type": event.get("card"),

            "own_goal": event.get("ownGoal"),
            "missed_penalty_outcome": event.get("missedPenaltyOutcome"),

            "assist": event.get("assistStr"),

            "home_score_at_event": event.get("homeScore"),
            "away_score_at_event": event.get("awayScore"),

            "home_score_after_event": home_score_after,
            "away_score_after_event": away_score_after,

            "period_label": event.get("halfStrShort"),

            "is_penalty_shootout": event.get("isPenaltyShootoutEvent")

        })

    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError(
            "No match events were extracted."
        )

    # --------------------------------------------------------
    # SAVE DATASET
    # --------------------------------------------------------

    output_file = output_dir / "match_events.csv"

    df.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # VALIDATION AND REPORTING
    # --------------------------------------------------------

    print("\nMATCH EVENTS TRANSFORMATION COMPLETE")
    print("=" * 60)

    print("\nDataset shape:")
    print(df.shape)

    print("\nEvent types:")
    print(df["event_type"].value_counts())

    print("\nGoal events:")

    print(
        df[df["event_type"] == "Goal"][
            [
                "display_minute",
                "player_name",
                "home_score_at_event",
                "away_score_at_event",
                "home_score_after_event",
                "away_score_after_event"
            ]
        ].to_string(index=False)
    )

    print("\nSubstitution events:")

    print(
        df[df["event_type"] == "Substitution"][
            [
                "display_minute",
                "team_name",
                "incoming_player",
                "outgoing_player"
            ]
        ].to_string(index=False)
    )

    print("\nCard events:")

    print(
        df[df["event_type"] == "Card"][
            [
                "display_minute",
                "team_name",
                "player_name",
                "card_type"
            ]
        ].to_string(index=False)
    )

    print("\nMissing values:")
    print(df.isnull().sum())

    print(f"\nSaved to: {output_file}")

    return df


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_match_events()
