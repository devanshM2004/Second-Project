# ============================================================
# src/flag_risks.py
# ============================================================
# PURPOSE:
#   Read the reconciliation results and assign a RISK_LEVEL to
#   every row using a transparent, rule-based scoring model.
#   Also attach a plain-English RECOMMENDED_ACTION so an analyst
#   knows exactly what to do with each flagged item.
#
# ── SCORING MODEL ────────────────────────────────────────────
#
#   Rule 1 – Discrepancy type (what kind of problem is it?)
#     BANK_ONLY        → +3 pts  bank recorded money the system missed
#     SYSTEM_ONLY      → +3 pts  system has an entry the bank never sent
#     AMOUNT_MISMATCH  → +2 pts  same transaction, different dollar value
#     DATE_MISMATCH    → +1 pt   same transaction, different posting date
#     MATCHED          → +0 pts  no issue
#
#   Rule 2 – Variance size (how much money is at stake?)
#     |variance| >= 10 000  → +3 pts  large exposure
#     |variance| >= 1 000   → +2 pts  moderate exposure
#     |variance| >= 100     → +1 pt   minor exposure
#
#   Rule 3 – Duplicate transaction detected
#     is_duplicate == True  → +2 pts  double-posting risk
#
#   Rule 4 – Repeat offender account
#     Account has 3+ discrepancies in this cycle → +2 pts
#     Account has 2   discrepancies in this cycle → +1 pt
#     (Rewards analysts for spotting systemic account-level issues)
#
#   ── Score → Risk level ──────────────────────────────────────
#     score >= 6  → HIGH    (immediate escalation required)
#     score 3–5   → MEDIUM  (investigate this cycle)
#     score <= 2  → LOW     (monitor, no urgent action)
#
# ── RECOMMENDED ACTIONS ──────────────────────────────────────
#   Assigned per (status × risk_level) combination so the action
#   is specific, not generic.
#
# OUTPUTS:
#   output/risk_flags.csv
#       All rows from reconciled_transactions.csv enriched with:
#           risk_score, risk_level, recommended_action
#       Sorted HIGH → MEDIUM → LOW, then by |variance| descending.
# ============================================================

import pandas as pd
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

# ── Action lookup table ───────────────────────────────────────
# Keys are (status, risk_level) tuples.
# Used by assign_actions() to attach a plain-English next step.
ACTION_MAP = {
    ("BANK_ONLY",       "HIGH"):   "Escalate immediately – large unrecorded bank debit/credit; investigate for fraud or processing failure",
    ("BANK_ONLY",       "MEDIUM"): "Raise exception ticket – locate missing system entry and post correcting journal",
    ("BANK_ONLY",       "LOW"):    "Log for end-of-cycle review – verify whether system posting is pending",

    ("SYSTEM_ONLY",     "HIGH"):   "Escalate immediately – phantom system entry with no bank confirmation; possible fictitious transaction",
    ("SYSTEM_ONLY",     "MEDIUM"): "Raise exception ticket – contact bank to confirm whether transaction was received",
    ("SYSTEM_ONLY",     "LOW"):    "Log for end-of-cycle review – confirm timing; may be in-transit item",

    ("AMOUNT_MISMATCH", "HIGH"):   "Escalate immediately – large dollar variance; request bank statement copy and audit system posting",
    ("AMOUNT_MISMATCH", "MEDIUM"): "Raise exception ticket – obtain source documents from both sides and post variance adjustment",
    ("AMOUNT_MISMATCH", "LOW"):    "Log for end-of-cycle review – likely rounding or FX conversion; verify and adjust if material",

    ("DATE_MISMATCH",   "HIGH"):   "Escalate – date gap exceeds tolerance on high-value item; check for cutoff manipulation",
    ("DATE_MISMATCH",   "MEDIUM"): "Investigate posting cutoff – confirm correct value date and amend system record if needed",
    ("DATE_MISMATCH",   "LOW"):    "Monitor – minor date shift, likely cutoff timing; confirm in next statement",

    ("MATCHED",         "HIGH"):   "Review duplicate flag – matched amount/date but duplicate ID detected; verify only one settlement occurred",
    ("MATCHED",         "MEDIUM"): "Review duplicate flag – matched but flagged as duplicate; confirm no double-posting",
    ("MATCHED",         "LOW"):    "No action required",
}


# ── Step 1: load ──────────────────────────────────────────────

def load_reconciliation_results() -> pd.DataFrame:
    """
    Read output/reconciled_transactions.csv written by reconcile.py.
    Raises FileNotFoundError if reconcile.py has not been run yet.
    """
    path = os.path.join(OUTPUT_DIR, "reconciled_transactions.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing file: {path}\n"
            "Run `python src/reconcile.py` first."
        )

    df = pd.read_csv(path, dtype=str)

    # Re-cast numeric columns that were saved as strings by to_csv
    df["bank_amount"]  = pd.to_numeric(df["bank_amount"],  errors="coerce")
    df["sys_amount"]   = pd.to_numeric(df["sys_amount"],   errors="coerce")
    df["variance"]     = pd.to_numeric(df["variance"],     errors="coerce")
    df["is_duplicate"] = df["is_duplicate"].str.upper() == "TRUE"

    print(f"  Loaded {len(df)} reconciled rows")
    return df


# ── Step 2: account-level repeat-offender counts ─────────────

def build_account_discrepancy_counts(df: pd.DataFrame) -> pd.Series:
    """
    Count how many non-MATCHED rows each account_id has.
    Returns a Series indexed by account_id.

    An account with many discrepancies in a single cycle is a
    systemic risk signal – something may be wrong with how that
    account is being processed, not just with individual transactions.
    """
    discrepancies = df[df["status"] != "MATCHED"]
    return discrepancies.groupby("account_id").size()


# ── Step 3: score each row ────────────────────────────────────

def score_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the four scoring rules to every row and add:
        risk_score  – integer 0–10
        risk_level  – HIGH / MEDIUM / LOW

    The function is intentionally written as explicit loops so
    the logic is easy to read and explain step-by-step.
    """
    # Pre-compute account discrepancy counts (Rule 4)
    account_counts = build_account_discrepancy_counts(df)

    # ── Rule 1 weights ────────────────────────────────────────
    status_points = {
        "BANK_ONLY":       3,
        "SYSTEM_ONLY":     3,
        "AMOUNT_MISMATCH": 2,
        "DATE_MISMATCH":   1,
        "MATCHED":         0,
    }

    scores = []

    for _, row in df.iterrows():
        score = 0

        # Rule 1 – discrepancy type
        score += status_points.get(row["status"], 0)

        # Rule 2 – variance magnitude
        abs_var = abs(row["variance"]) if pd.notna(row["variance"]) else 0
        if abs_var >= 10_000:
            score += 3
        elif abs_var >= 1_000:
            score += 2
        elif abs_var >= 100:
            score += 1

        # Rule 3 – duplicate flag
        if row["is_duplicate"]:
            score += 2

        # Rule 4 – repeat offender account
        account_disc_count = account_counts.get(row["account_id"], 0)
        if account_disc_count >= 3:
            score += 2
        elif account_disc_count == 2:
            score += 1

        scores.append(score)

    df = df.copy()
    df["risk_score"] = scores

    # Map score to risk level
    df["risk_level"] = df["risk_score"].apply(
        lambda s: "HIGH" if s >= 6 else ("MEDIUM" if s >= 3 else "LOW")
    )

    return df


# ── Step 4: attach recommended actions ───────────────────────

def assign_actions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Look up the recommended action for each row using the
    (status, risk_level) pair as a key into ACTION_MAP.

    Falls back to a generic message if a combination isn't in the map
    (defensive coding – shouldn't happen with known statuses).
    """
    df = df.copy()

    df["recommended_action"] = df.apply(
        lambda row: ACTION_MAP.get(
            (row["status"], row["risk_level"]),
            "Review manually"           # fallback
        ),
        axis=1,
    )

    return df


# ── Step 5: sort output ───────────────────────────────────────

def sort_by_priority(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sort so the most urgent items appear at the top of the file:
        Primary   – risk_level  (HIGH → MEDIUM → LOW)
        Secondary – |variance|  (largest exposure first)
        Tertiary  – status      (BANK_ONLY / SYSTEM_ONLY before mismatches)
    """
    level_order  = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    status_order = {"BANK_ONLY": 0, "SYSTEM_ONLY": 1,
                    "AMOUNT_MISMATCH": 2, "DATE_MISMATCH": 3, "MATCHED": 4}

    df = df.copy()
    df["_level_sort"]  = df["risk_level"].map(level_order)
    df["_status_sort"] = df["status"].map(status_order)
    df["_abs_var"]     = df["variance"].abs().fillna(0)

    df = df.sort_values(
        ["_level_sort", "_abs_var", "_status_sort"],
        ascending=[True, False, True],
    ).drop(columns=["_level_sort", "_status_sort", "_abs_var"])

    return df.reset_index(drop=True)


# ── Orchestrator ──────────────────────────────────────────────

def run_risk_flagging():
    """
    Full risk-flagging pipeline:
      load → score → assign actions → sort → save
    Called by main.py Step 3.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load reconciliation results
    df = load_reconciliation_results()

    # 2. Score every row
    df = score_risk(df)

    # 3. Attach plain-English recommended actions
    df = assign_actions(df)

    # 4. Sort highest priority to the top
    df = sort_by_priority(df)

    # 5. Save
    output_path = os.path.join(OUTPUT_DIR, "risk_flags.csv")
    df.to_csv(output_path, index=False)
    print(f"  Saved: {os.path.abspath(output_path)}  ({len(df)} rows)")

    # ── Terminal summary ──────────────────────────────────────
    print("\n  Risk level breakdown:")
    counts = df["risk_level"].value_counts()
    total  = len(df)
    for level in ["HIGH", "MEDIUM", "LOW"]:
        n = counts.get(level, 0)
        print(f"    {level:<8} {n:>3}  ({n/total*100:.1f}%)")

    print("\n  Top 5 highest-risk transactions:")
    cols = ["transaction_id", "account_name", "status",
            "variance", "risk_score", "risk_level"]
    print(df[cols].head(5).to_string(index=False))

    return df


# Allow running this file directly for testing
if __name__ == "__main__":
    run_risk_flagging()
