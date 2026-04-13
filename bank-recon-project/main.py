# main.py  -  Bank Reconciliation and Risk Detection Model
#
# Run this file to execute the full pipeline from start to finish.
# It calls each script in order and saves all outputs to output/.
#
#   Step 1 - generate_data.py  : build the fake transaction data
#   Step 2 - reconcile.py      : compare bank vs system records
#   Step 3 - flag_risks.py     : score and flag each discrepancy
#   Step 4 - summary.py        : roll up results by account
#   Step 5 - report.py         : export the HIGH-risk action list
#
# Usage:  python main.py

from src.generate_data import generate_all
from src.reconcile     import run_reconciliation
from src.flag_risks    import run_risk_flagging
from src.summary       import run_summary
from src.report        import run_report


def main():
    print("=" * 55)
    print("  Bank Reconciliation and Risk Detection Model")
    print("=" * 55)

    # ── Step 1 ───────────────────────────────────────────────
    # Create three synthetic CSV files in data/:
    #   accounts.csv, bank_transactions.csv, system_transactions.csv
    # Intentional data quality issues are injected here.
    print("\n[Step 1] Generating synthetic data...")
    generate_all()

    # ── Step 2 ───────────────────────────────────────────────
    # Outer-join bank and system records on transaction_id.
    # Classify each row: MATCHED / AMOUNT_MISMATCH / DATE_MISMATCH
    #                    / BANK_ONLY / SYSTEM_ONLY
    # Outputs: reconciled_transactions.csv, discrepancy_report.csv
    print("\n[Step 2] Running reconciliation...")
    run_reconciliation()

    # ── Step 3 ───────────────────────────────────────────────
    # Apply four scoring rules to every reconciled row.
    # Assign risk_level (HIGH / MEDIUM / LOW) and a recommended action.
    # Output: risk_flags.csv
    print("\n[Step 3] Flagging risks...")
    run_risk_flagging()

    # ── Step 4 ───────────────────────────────────────────────
    # Aggregate to one row per account:
    #   total transactions, discrepancy count & rate,
    #   total variance exposure, highest risk level reached.
    # Outputs: summary_report.csv, summary_report.txt
    print("\n[Step 4] Building account summary...")
    run_summary()

    # ── Step 5 ───────────────────────────────────────────────
    # Filter to HIGH-risk rows only and save as an action list
    # for same-day escalation.
    # Output: high_risk_transactions.csv
    print("\n[Step 5] Exporting high-risk action list...")
    run_report()

    # ── Done ─────────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  Pipeline complete. Output files:")
    print("    output/reconciled_transactions.csv")
    print("    output/discrepancy_report.csv")
    print("    output/risk_flags.csv")
    print("    output/summary_report.csv")
    print("    output/summary_report.txt")
    print("    output/high_risk_transactions.csv")
    print("=" * 55)


if __name__ == "__main__":
    main()
