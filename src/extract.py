import requests
import json
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MATCH_ID = 6040239

MATCH_URL = (
    "https://www.fotmob.com/matches/"
    "ghana-vs-somalia/jy48rbo"
)

RAW_DIR = BASE_DIR / "data" / "raw"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.fotmob.com/"
}

def extract_match_details(
    match_id=MATCH_ID,
    output_dir=RAW_DIR
):

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"match_details_{match_id}.json"

    print("\nFOTMOB MATCH DATA EXTRACTION")
    print("=" * 60)

    # --------------------------------------------------------
    # REUSE EXISTING RAW DATA IF AVAILABLE
    # --------------------------------------------------------

    if output_file.exists():

        print("Existing raw match file found.")
        print("Checking match identity...")

        with open(output_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        page_props = data.get("props", {}).get(
            "pageProps", {}
        )

        general = page_props.get("general", {})

        extracted_match_id = general.get("matchId")
        home_team = general.get("homeTeam", {}).get("name")
        away_team = general.get("awayTeam", {}).get("name")
        match_date = general.get("matchTimeUTCDate", "")

        if str(extracted_match_id) != str(match_id):
            raise ValueError(
                f"Existing raw file has incorrect match ID: "
                f"{extracted_match_id}"
            )

        if home_team != "Ghana" or away_team != "Somalia":
            raise ValueError(
                "Existing raw file does not match Ghana vs Somalia."
            )

        if not match_date.startswith("2026-11-12"):
            raise ValueError(
                f"Unexpected match date: {match_date}"
            )

        print("Verified existing raw match data.")
        print("Match ID:", extracted_match_id)
        print("Match:", general.get("matchName"))
        print("Source: Existing local raw JSON")

        return data

    # --------------------------------------------------------
    # EXTRACT FROM FOTMOB IF NO VERIFIED FILE EXISTS
    # --------------------------------------------------------

    print("No existing raw file found.")
    print("Fetching FotMob match page...")

    response = requests.get(
        MATCH_URL,
        headers=HEADERS,
        timeout=30
    )

    print("HTTP Status:", response.status_code)
    print("Final URL:", response.url)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    script = soup.find(
        "script",
        id="__NEXT_DATA__"
    )

    if script is None:
        raise ValueError(
            "Could not find embedded FotMob JSON."
        )

    data = json.loads(
        script.string or script.get_text()
    )

    page_props = data.get("props", {}).get(
        "pageProps", {}
    )

    general = page_props.get("general", {})

    extracted_match_id = general.get("matchId")

    # --------------------------------------------------------
    # VALIDATE MATCH ID AND IDENTITY
    # --------------------------------------------------------

    if str(extracted_match_id) != str(match_id):
        raise ValueError(
            f"Match ID mismatch. Expected {match_id}, "
            f"received {extracted_match_id}. "
            "Raw data was not saved."
        )

    if (
        general.get("homeTeam", {}).get("name") != "Ghana"
        or general.get("awayTeam", {}).get("name") != "Somalia"
    ):
        raise ValueError(
            "The returned fixture is not Ghana vs Somalia."
        )

    if not general.get("matchTimeUTCDate", "").startswith("2026-11-12"):
        raise ValueError(
            "The returned match date is not 12 November 2026."
        )

    content = page_props.get("content", {})

    if not content:
        raise ValueError(
            "Match content was not pre-rendered."
        )

    # --------------------------------------------------------
    # SAVE VERIFIED RAW JSON
    # --------------------------------------------------------

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nJSON successfully extracted!")
    print("Saved:", output_file)

    print("\nMATCH METADATA")
    print("-" * 60)

    print("Match ID:", general.get("matchId"))
    print("Match:", general.get("matchName"))
    print("Competition:", general.get("leagueName"))

    player_stats = content.get("playerStats", {})

    print("\nPlayer records:", len(player_stats))
    print("\nEXTRACTION COMPLETED")

    return data
