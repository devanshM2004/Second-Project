# ============================================================
# src/report.py
# ============================================================
# PURPOSE:
#   Final step in the pipeline. Reads risk_flags.csv and exports
#   a filtered action list for the operations team:
#
#   output/high_risk_transactions.csv
#       Only HIGH-risk rows, sorted by |variance| descending.
#       This is the file an analyst hands to their manager for
#       same-day escalation.
#
# NOTE:
#   The broader executive summary (all accounts, all risk levels,
#   plain-text report) is produced by src/summary.py.
#   This file focuses solely on the HIGH-risk action list.
# ============================================================

import pandas as pd
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def load_risk_flags() -> pd.DataFrame:
    """
    Read output/risk_flags.csv produced by flag_risks.py.
    Raises FileNotFoundError if the file is missing.
    """
    path = os.path.join(OUTPUT_DIR, "risk_flags.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing file: {path}\n"
            "Run `python src/flag_risks.py` first."
        )

    df = pd.read_csv(path, dtype=str)
    df["variance"]   = pd.to_numeric(df["variance"],   errors="coerce")
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce")
    return df


def run_report():
    """
    Filter to HIGH-risk rows, sort by |variance|, and save.
    Called by main.py Step 5.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    flagged_df = load_risk_flags()

    # Keep only HIGH-risk rows and sort largest variance first
    high_risk_df = (
        flagged_df[flagged_df["risk_level"] == "HIGH"]
        .copy()
        .assign(abs_var=lambda d: d["variance"].abs())
        .sort_values("abs_var", ascending=False)
        .drop(columns="abs_var")
        .reset_index(drop=True)
    )

    output_path = os.path.join(OUTPUT_DIR, "high_risk_transactions.csv")
    high_risk_df.to_csv(output_path, index=False)
    print(f"  Saved: {os.path.abspath(output_path)}  ({len(high_risk_df)} rows)")
    print(f"  High-risk items requiring immediate review: {len(high_risk_df)}")


# Allow running this file directly for testing
if __name__ == "__main__":
    run_report()
