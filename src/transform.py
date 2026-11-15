
import json
import pandas as pd

from pathlib import Path


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "match_details_6040239.json"

OUTPUT_DIR = BASE_DIR / "data" / "processed"


# ============================================================
# TRANSFORM TEAM STATISTICS
# ============================================================

def transform_team_statistics(
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
    # LOAD RAW DATA
    # --------------------------------------------------------

    with open(
        raw_file,
        "r",
        encoding="utf-8"
    ) as file:

        raw = json.load(file)

    content = raw["props"]["pageProps"]["content"]

    team_stats = content["stats"]["Periods"]

    # --------------------------------------------------------
    # TRANSFORM TEAM STATISTICS
    # --------------------------------------------------------

    teams = ["Ghana", "Somalia"]

    records = []

    for period_name, period_data in team_stats.items():

        for category in period_data.get("stats", []):

            category_name = category.get("title")

            for metric in category.get("stats", []):

                metric_name = metric.get("title")
                values = metric.get("stats", [])

                # Skip category heading rows
                if len(values) != 2:
                    continue

                if values == [None, None]:
                    continue

                records.append({
                    "period": period_name,
                    "category": category_name,
                    "metric": metric_name,
                    "home_team": teams[0],
                    "away_team": teams[1],
                    "home_value": values[0],
                    "away_value": values[1]
                })

    # --------------------------------------------------------
    # CREATE DATAFRAME
    # --------------------------------------------------------

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError(
            "No team statistics were extracted."
        )

    # --------------------------------------------------------
    # SAVE PROCESSED DATA
    # --------------------------------------------------------

    output_file = output_dir / "team_statistics.csv"

    df.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # VALIDATION AND REPORTING
    # --------------------------------------------------------

    print("\nTEAM STATISTICS TRANSFORMATION COMPLETE")
    print("=" * 60)

    print("\nDataset shape:")
    print(df.shape)

    print("\nPeriods:")
    print(df["period"].unique())

    print("\nCategories:")
    print(df["category"].unique())

    print("\nSample records:")
    print(df.head(10).to_string(index=False))

    print("\nMissing values:")
    print(df.isnull().sum())

    print(f"\nSaved to: {output_file}")

    return df


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_team_statistics()
