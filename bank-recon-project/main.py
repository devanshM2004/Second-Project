# ============================================================
# main.py  –  Bank Reconciliation and Risk Detection Model
# ============================================================
# Entry point for the full pipeline.
# Run this file to execute every step in order:
#   1. Generate synthetic CSV data
#   2. Reconcile bank vs system transactions
#   3. Flag risk items
#   4. Produce a summary report
# ============================================================

from src.generate_data import generate_all
from src.reconcile import run_reconciliation
from src.flag_risks import run_risk_flagging
from src.report import run_report


def main():
    print("=" * 55)
    print("  Bank Reconciliation and Risk Detection Model")
    print("=" * 55)

    # Step 1 – Create synthetic data files in data/
    print("\n[Step 1] Generating synthetic data...")
    generate_all()

    # Step 2 – Compare bank records vs internal system records
    print("\n[Step 2] Running reconciliation...")
    run_reconciliation()

    # Step 3 – Score and flag high-risk discrepancies
    print("\n[Step 3] Flagging risks...")
    run_risk_flagging()

    # Step 4 – Write summary report to output/
    print("\n[Step 4] Generating summary report...")
    run_report()

    print("\nDone. Check the output/ folder for results.")


if __name__ == "__main__":
    main()
