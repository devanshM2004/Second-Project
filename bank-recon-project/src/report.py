# ============================================================
# src/report.py
# ============================================================
# PURPOSE:
#   Consume the risk_flags.csv and produce two human-readable
#   output files that an analyst would hand off to a manager:
#
#   output/summary_report.txt
#       Plain-text executive summary with key metrics:
#         - Total transactions reviewed
#         - Count & % by reconciliation status
#         - Count & % by risk level
#         - Total variance ($ exposed)
#         - Top 5 highest-variance transactions
#
#   output/high_risk_transactions.csv
#       Filtered view of only HIGH risk rows so the team
#       can action them immediately.
#
# ============================================================

import pandas as pd
import os
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def load_risk_flags():
    """
    Read output/risk_flags.csv produced by flag_risks.py.
    """
    # TODO: load and return the DataFrame
    pass


def build_summary_text(flagged_df):
    """
    Compute aggregate stats and format them into a multi-line
    plain-text string suitable for saving as a .txt report.
    Returns the formatted string.
    """
    # TODO: compute stats and build the report text
    pass


def run_report():
    """
    Load risk flags → build summary → save both output files.
    Called by main.py Step 4.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    flagged_df = load_risk_flags()

    # --- Plain-text summary ---
    summary_text = build_summary_text(flagged_df)
    summary_path = os.path.join(OUTPUT_DIR, "summary_report.txt")
    with open(summary_path, "w") as f:
        f.write(summary_text)
    print(f"  Saved: {os.path.abspath(summary_path)}")

    # --- High-risk CSV ---
    high_risk_df = flagged_df[flagged_df["risk_level"] == "HIGH"]
    high_risk_path = os.path.join(OUTPUT_DIR, "high_risk_transactions.csv")
    high_risk_df.to_csv(high_risk_path, index=False)
    print(f"  Saved: {os.path.abspath(high_risk_path)}")
    print(f"  High-risk items requiring review: {len(high_risk_df)}")
