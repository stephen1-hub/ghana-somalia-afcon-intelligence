
import sqlite3
import json

from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
INTELLIGENCE_DIR = PROCESSED_DIR / "match_intelligence"

DATABASE_DIR = BASE_DIR / "data" / "database"
DATABASE_PATH = DATABASE_DIR / "ghana_somalia_intelligence.db"


def load_processed_data(
    processed_dir=PROCESSED_DIR,
    database_path=DATABASE_PATH
):

    processed_dir = Path(processed_dir)
    database_path = Path(database_path)

    if not processed_dir.exists():
        raise FileNotFoundError(
            f"Processed data directory not found: {processed_dir}"
        )

    csv_files = sorted(processed_dir.glob("*.csv"))

    intelligence_csv_files = sorted(
        (processed_dir / "match_intelligence").glob("*.csv")
    )

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {processed_dir}"
        )

    database_path.parent.mkdir(parents=True, exist_ok=True)

    load_records = []

    print("\nDATABASE LOADING")
    print("=" * 60)

    with sqlite3.connect(database_path) as connection:

        # ------------------------------------------
        # 1. Load main processed CSV datasets
        # ------------------------------------------

        all_csv_files = csv_files + intelligence_csv_files

        for csv_file in all_csv_files:

            table_name = csv_file.stem

            dataframe = pd.read_csv(csv_file)

            dataframe.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False
            )

            loaded_rows = pd.read_sql_query(
                f'SELECT COUNT(*) AS row_count FROM "{table_name}"',
                connection
            ).iloc[0]["row_count"]

            load_records.append({
                "table_name": table_name,
                "source_file": str(
                    csv_file.relative_to(processed_dir)
                ),
                "rows_loaded": int(loaded_rows),
                "columns_loaded": len(dataframe.columns),
                "loaded_at": datetime.now(timezone.utc).isoformat()
            })

            print(
                f"Loaded {table_name}: "
                f"{loaded_rows} rows, "
                f"{len(dataframe.columns)} columns"
            )

        # ------------------------------------------
        # 2. Load match intelligence JSON summary
        # ------------------------------------------

        summary_file = (
            processed_dir
            / "match_intelligence"
            / "match_intelligence_summary.json"
        )

        if not summary_file.exists():
            raise FileNotFoundError(
                f"Match intelligence summary not found: {summary_file}"
            )

        with open(summary_file, "r", encoding="utf-8") as file:
            summary_data = json.load(file)

        summary_dataframe = pd.DataFrame([{
            "summary_json": json.dumps(summary_data)
        }])

        summary_dataframe.to_sql(
            "match_intelligence_summary",
            connection,
            if_exists="replace",
            index=False
        )

        load_records.append({
            "table_name": "match_intelligence_summary",
            "source_file": str(
                summary_file.relative_to(processed_dir)
            ),
            "rows_loaded": 1,
            "columns_loaded": 1,
            "loaded_at": datetime.now(timezone.utc).isoformat()
        })

        print(
            "Loaded match_intelligence_summary: "
            "1 row, 1 column"
        )

        # ------------------------------------------
        # 3. Create database load audit
        # ------------------------------------------

        load_audit = pd.DataFrame(load_records)

        load_audit.to_sql(
            "load_audit",
            connection,
            if_exists="replace",
            index=False
        )

    print("\nDATABASE LOAD COMPLETE")
    print("=" * 60)

    print("Tables loaded:", len(load_records))
    print("Database:", database_path)

    return {
        "status": "passed",
        "tables_loaded": len(load_records),
        "database_path": str(database_path),
        "load_audit": load_audit
    }


if __name__ == "__main__":
    load_processed_data()
