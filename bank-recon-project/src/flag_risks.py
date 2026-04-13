# ============================================================
# src/flag_risks.py
# ============================================================
# PURPOSE:
#   Read the reconciliation results and assign a RISK_LEVEL
#   (HIGH / MEDIUM / LOW) to each discrepancy based on a simple
#   rule-based scoring model.
#
# RISK RULES (beginner-friendly, easy to explain in interviews):
#
#   Rule 1 – Status weight
#     BANK_ONLY   → +3 points  (money the bank shows but system missed)
#     SYSTEM_ONLY → +3 points  (phantom system entry)
#     AMOUNT_MISMATCH → +2 points
#     DATE_MISMATCH   → +1 point
#     MATCHED         → 0 points
#
#   Rule 2 – Large variance penalty
#     abs(variance) >= 5 000 → +2 extra points
#     abs(variance) >= 1 000 → +1 extra point
#
#   Rule 3 – Duplicate flag
#     If the transaction_id appears more than once → +2 points
#
#   Final mapping:
#     score >= 5 → HIGH
#     score 3–4  → MEDIUM
#     score <= 2 → LOW
#
# OUTPUT:
#   output/risk_flags.csv
#       Reconciliation results enriched with 'risk_score'
#       and 'risk_level' columns.
# ============================================================

import pandas as pd
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def load_reconciliation_results():
    """
    Read output/reconciliation_results.csv produced by reconcile.py.
    """
    # TODO: load and return the DataFrame
    pass


def score_risk(results_df):
    """
    Apply the rule-based scoring model described above.
    Returns the DataFrame with 'risk_score' and 'risk_level' added.
    """
    # TODO: implement scoring rules
    pass


def run_risk_flagging():
    """
    Load reconciliation results → score → save risk_flags.csv.
    Called by main.py Step 3.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results_df = load_reconciliation_results()
    flagged_df = score_risk(results_df)

    output_path = os.path.join(OUTPUT_DIR, "risk_flags.csv")
    flagged_df.to_csv(output_path, index=False)
    print(f"  Saved: {os.path.abspath(output_path)}")

    # Quick summary for the terminal
    counts = flagged_df["risk_level"].value_counts()
    for level in ["HIGH", "MEDIUM", "LOW"]:
        print(f"  {level}: {counts.get(level, 0)}")
