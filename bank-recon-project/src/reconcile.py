# ============================================================
# src/reconcile.py
# ============================================================
# PURPOSE:
#   Compare the bank transaction file against the internal
#   system transaction file and classify every row into one
#   of four reconciliation statuses:
#
#   MATCHED        – transaction_id exists in both sources
#                    AND amount AND date are identical
#   AMOUNT_MISMATCH– transaction_id found in both, but the
#                    posted amount differs
#   DATE_MISMATCH  – transaction_id found in both, but the
#                    posting date differs
#   BANK_ONLY      – transaction_id exists in bank file only
#                    (system never recorded it → potential loss)
#   SYSTEM_ONLY    – transaction_id exists in system file only
#                    (bank never reported it → phantom entry)
#
# OUTPUT:
#   output/reconciliation_results.csv
#       One row per transaction with a 'status' column and a
#       'variance' column showing the amount difference.
# ============================================================

import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def load_data():
    """
    Read the three CSVs from data/ and return them as DataFrames.
    Raises FileNotFoundError if generate_data has not been run first.
    """
    # TODO: load accounts.csv, bank_transactions.csv,
    #       system_transactions.csv and return them
    pass


def merge_transactions(bank_df, system_df):
    """
    Outer-join bank and system DataFrames on transaction_id.
    Suffix _bank and _sys distinguish columns from each source.
    Returns a merged DataFrame ready for status classification.
    """
    # TODO: perform the outer merge
    pass


def classify_status(merged_df):
    """
    Walk the merged DataFrame row-by-row and assign a status
    string to each record based on which fields match.
    Also calculate 'variance' = bank_amount - system_amount.
    Returns the DataFrame with 'status' and 'variance' columns added.
    """
    # TODO: implement status classification logic
    pass


def run_reconciliation():
    """
    Full reconciliation pipeline:
      load → merge → classify → save
    Called by main.py Step 2.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    bank_df, system_df, accounts_df = load_data()
    merged_df = merge_transactions(bank_df, system_df)
    results_df = classify_status(merged_df)

    output_path = os.path.join(OUTPUT_DIR, "reconciliation_results.csv")
    results_df.to_csv(output_path, index=False)
    print(f"  Saved: {os.path.abspath(output_path)}")
    print(f"  Total records: {len(results_df)}")
