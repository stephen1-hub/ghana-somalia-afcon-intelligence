
from src.extract import extract_match_details

from src.transform import transform_team_statistics
from src.transform_events import transform_match_events
from src.transform_lineups import transform_lineups
from src.transform_players import transform_player_statistics

from src.reconcile_appearances import reconcile_appearances
from src.build_reconciled_appearances import build_reconciled_appearances

from src.analyse_match import run_match_analysis
from src.build_match_timeline import build_match_timeline
from src.build_match_intelligence import build_match_intelligence

from src.validate_pipeline import validate_pipeline
from src.validate_dashboard_data import validate_dashboard_data

from src.load import load_processed_data


def main():

    print("=" * 65)
    print("GHANA VS SOMALIA — FULL MATCH INTELLIGENCE ETL PIPELINE")
    print("=" * 65)

    # --------------------------------------------------------
    # 1. EXTRACT
    # --------------------------------------------------------

    print("\n[1/13] Extracting raw FotMob match data...")
    extract_match_details()

    # --------------------------------------------------------
    # 2. TRANSFORM
    # --------------------------------------------------------

    print("\n[2/13] Transforming team statistics...")
    transform_team_statistics()

    print("\n[3/13] Transforming match events...")
    transform_match_events()

    print("\n[4/13] Transforming lineups...")
    transform_lineups()

    print("\n[5/13] Transforming player statistics...")
    transform_player_statistics()

    # --------------------------------------------------------
    # 3. RECONCILIATION
    # --------------------------------------------------------

    print("\n[6/13] Reconciling player appearance records...")
    reconcile_appearances()

    print("\n[7/13] Building canonical reconciled appearances...")
    build_reconciled_appearances()

    # --------------------------------------------------------
    # 4. ANALYSIS AND INTELLIGENCE
    # --------------------------------------------------------

    print("\n[8/13] Running match analysis...")
    run_match_analysis()

    print("\n[9/13] Building match timeline...")
    build_match_timeline()

    print("\n[10/13] Building match intelligence...")
    build_match_intelligence()

    # --------------------------------------------------------
    # 5. VALIDATION
    # --------------------------------------------------------

    print("\n[11/13] Validating source and processed datasets...")
    pipeline_result = validate_pipeline()

    if pipeline_result["status"] != "passed":
        raise SystemExit(
            "Pipeline validation failed. Stopping execution."
        )

    print("\n[12/13] Validating dashboard data...")
    dashboard_result = validate_dashboard_data()

    if dashboard_result["status"] != "passed":
        raise SystemExit(
            "Dashboard validation failed. Stopping execution."
        )

    # --------------------------------------------------------
    # 6. LOAD
    # --------------------------------------------------------

    print("\n[13/13] Loading processed datasets into SQLite...")
    load_result = load_processed_data()

    if load_result["status"] != "passed":
        raise SystemExit(
            "Database loading failed. Stopping execution."
        )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("FULL ETL PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 65)

    print("Extraction:       Completed")
    print("Transformation:   Completed")
    print("Reconciliation:   Completed")
    print("Analysis:         Completed")
    print("Intelligence:     Completed")
    print("Validation:       Passed")
    print("Database loading: Completed")

    print("\nDatabase location:")
    print(load_result["database_path"])


if __name__ == "__main__":
    main()
