
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"


def describe_event(row):
    """Convert a match event into a readable timeline description."""

    event_type = row["event_type"]
    team = row["team_name"]
    player = row["player_name"]

    if event_type == "Goal":
        return f"GOAL - {player} ({team})"

    elif event_type == "MissedPenalty":
        return f"PENALTY MISSED - {player} ({team})"

    elif event_type == "Card":
        return f"{row['card_type']} CARD - {player} ({team})"

    elif event_type == "Substitution":
        return (
            f"SUBSTITUTION - {team}: "
            f"{row['incoming_player']} ON, "
            f"{row['outgoing_player']} OFF"
        )

    elif event_type == "Half":
        return f"{row['period_label']}"

    return str(event_type)


def build_match_timeline(data_dir=DATA_DIR):
    """Build and export the chronological match event timeline."""

    data_dir = Path(data_dir)
    events_path = data_dir / "match_events.csv"

    if not events_path.exists():
        raise FileNotFoundError(
            f"Match events file not found: {events_path}"
        )

    events = pd.read_csv(events_path)

    if events.empty:
        raise ValueError("Match events file contains no events.")

    timeline = events.copy()

    # Create readable event descriptions
    timeline["event_description"] = timeline.apply(
        describe_event,
        axis=1
    )

    # Build score after each event
    timeline["score_after_event"] = (
        timeline["home_score_after_event"].astype(str)
        + " - "
        + timeline["away_score_after_event"].astype(str)
    )

    # Select final timeline columns
    output_columns = [
        "event_sequence",
        "display_minute",
        "event_type",
        "team_name",
        "player_name",
        "incoming_player",
        "outgoing_player",
        "event_description",
        "score_after_event"
    ]

    timeline = timeline[output_columns].copy()

    # Preserve original event order
    timeline = timeline.sort_values(
        "event_sequence"
    ).reset_index(drop=True)

    # Export timeline
    output_path = data_dir / "match_timeline.csv"

    timeline.to_csv(
        output_path,
        index=False
    )

    print("\nMATCH EVENT TIMELINE")
    print("=" * 75)
    print(timeline.to_string(index=False))
    print("\nTotal events:", len(timeline))
    print("Saved:", output_path)

    return timeline


if __name__ == "__main__":
    build_match_timeline()
