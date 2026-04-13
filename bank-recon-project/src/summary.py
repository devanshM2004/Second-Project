# summary.py
#
# This script rolls up the risk-flagged data into two outputs
# that are easy to read and share:
#
#   output/summary_report.csv
#       One row per account. Shows how many transactions each account
#       had, how many had problems, the total dollar variance, and the
#       highest risk level reached. Includes a TOTALS row at the bottom.
#
#   output/summary_report.txt
#       A plain-text report with overall stats, status breakdowns,
#       risk counts, the account table, and the top 5 items by variance.
#       The kind of thing you'd paste into an email to a manager.
#
# This runs after flag_risks.py in the pipeline.

import pandas as pd
import os
from datetime import date

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")

# Risk level ordering used for "highest risk" comparisons
RISK_ORDER = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}


# ── Step 1: load ──────────────────────────────────────────────

def load_data():
    """
    Read risk_flags.csv (output of flag_risks.py) and accounts.csv.
    Re-casts numeric and boolean columns that were serialised as strings.
    Returns (flagged_df, accounts_df).
    """
    flags_path    = os.path.join(OUTPUT_DIR, "risk_flags.csv")
    accounts_path = os.path.join(DATA_DIR,   "accounts.csv")

    for label, path in [("risk_flags", flags_path),
                        ("accounts",   accounts_path)]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing {label} file: {path}\n"
                "Run the earlier pipeline steps first."
            )

    flagged_df  = pd.read_csv(flags_path,    dtype=str)
    accounts_df = pd.read_csv(accounts_path, dtype=str)

    # Re-cast columns that pandas reads back as strings from CSV
    flagged_df["bank_amount"]  = pd.to_numeric(flagged_df["bank_amount"],  errors="coerce")
    flagged_df["sys_amount"]   = pd.to_numeric(flagged_df["sys_amount"],   errors="coerce")
    flagged_df["variance"]     = pd.to_numeric(flagged_df["variance"],     errors="coerce")
    flagged_df["risk_score"]   = pd.to_numeric(flagged_df["risk_score"],   errors="coerce")
    flagged_df["is_duplicate"] = flagged_df["is_duplicate"].str.upper() == "TRUE"

    print(f"  Loaded {len(flagged_df)} flagged rows across "
          f"{flagged_df['account_id'].nunique()} accounts")
    return flagged_df, accounts_df


# ── Step 2: build per-account summary table ───────────────────

def build_account_summary(flagged_df: pd.DataFrame,
                          accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate risk_flags.csv down to one row per account.

    Columns produced:
        account_id, account_name, account_type, account_status
        total_transactions   – all rows for this account
        discrepancy_count    – rows where status != MATCHED
        discrepancy_rate_pct – discrepancy_count / total * 100
        total_variance_usd   – sum of |variance| across discrepancies
        matched_count
        bank_only_count
        system_only_count
        amount_mismatch_count
        date_mismatch_count
        high_count, medium_count, low_count
        highest_risk_level   – worst level seen for this account
    """
    rows = []

    for account_id, group in flagged_df.groupby("account_id"):
        total       = len(group)
        disc_mask   = group["status"] != "MATCHED"
        disc_count  = disc_mask.sum()
        disc_rate   = round(disc_count / total * 100, 1) if total else 0

        # Sum absolute variances on non-matched rows only
        total_var   = round(group.loc[disc_mask, "variance"].abs().sum(), 2)

        # Per-status counts
        status_vc = group["status"].value_counts()
        matched_c = status_vc.get("MATCHED",         0)
        bank_c    = status_vc.get("BANK_ONLY",        0)
        sys_c     = status_vc.get("SYSTEM_ONLY",      0)
        amt_c     = status_vc.get("AMOUNT_MISMATCH",  0)
        date_c    = status_vc.get("DATE_MISMATCH",    0)

        # Per-risk-level counts
        risk_vc   = group["risk_level"].value_counts()
        high_c    = risk_vc.get("HIGH",   0)
        med_c     = risk_vc.get("MEDIUM", 0)
        low_c     = risk_vc.get("LOW",    0)

        # Highest risk level reached (only meaningful if discrepancies exist)
        if disc_count > 0:
            highest = group.loc[disc_mask, "risk_level"].map(RISK_ORDER).max()
            highest_level = {3: "HIGH", 2: "MEDIUM", 1: "LOW"}.get(highest, "LOW")
        else:
            highest_level = "LOW"

        rows.append({
            "account_id":            account_id,
            "total_transactions":    total,
            "discrepancy_count":     disc_count,
            "discrepancy_rate_pct":  disc_rate,
            "total_variance_usd":    total_var,
            "matched_count":         matched_c,
            "bank_only_count":       bank_c,
            "system_only_count":     sys_c,
            "amount_mismatch_count": amt_c,
            "date_mismatch_count":   date_c,
            "high_count":            high_c,
            "medium_count":          med_c,
            "low_count":             low_c,
            "highest_risk_level":    highest_level,
        })

    summary = pd.DataFrame(rows)

    # Join account metadata (name, type, status) from accounts.csv
    summary = summary.merge(accounts_df, on="account_id", how="left")

    # Reorder columns so identifying info comes first
    col_order = [
        "account_id", "account_name", "account_type", "status",
        "total_transactions", "discrepancy_count", "discrepancy_rate_pct",
        "total_variance_usd", "matched_count",
        "bank_only_count", "system_only_count",
        "amount_mismatch_count", "date_mismatch_count",
        "high_count", "medium_count", "low_count",
        "highest_risk_level",
    ]
    summary = summary[col_order]

    # Sort: highest risk first, then by total variance descending
    risk_sort = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    summary["_rsort"] = summary["highest_risk_level"].map(risk_sort)
    summary = summary.sort_values(
        ["_rsort", "total_variance_usd"], ascending=[True, False]
    ).drop(columns="_rsort").reset_index(drop=True)

    return summary


def append_totals_row(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Add a TOTALS row at the bottom of the account summary so a manager
    can see the full-portfolio figures at a glance.
    String columns get a placeholder; numeric columns are summed.
    The highest_risk_level in the totals row reflects the worst seen
    across all accounts.
    """
    numeric_cols = [
        "total_transactions", "discrepancy_count",
        "total_variance_usd", "matched_count",
        "bank_only_count", "system_only_count",
        "amount_mismatch_count", "date_mismatch_count",
        "high_count", "medium_count", "low_count",
    ]

    totals = {col: summary[col].sum() for col in numeric_cols}

    # Recalculate rate from the summed counts
    total_txn  = totals["total_transactions"]
    total_disc = totals["discrepancy_count"]
    totals["discrepancy_rate_pct"] = round(total_disc / total_txn * 100, 1) if total_txn else 0

    # Overall highest risk level
    if totals["high_count"] > 0:
        overall_risk = "HIGH"
    elif totals["medium_count"] > 0:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"

    totals.update({
        "account_id":         "TOTAL",
        "account_name":       "— All Accounts —",
        "account_type":       "",
        "status":             "",
        "highest_risk_level": overall_risk,
    })

    totals_row = pd.DataFrame([totals])[summary.columns]
    return pd.concat([summary, totals_row], ignore_index=True)


# ── Step 3: build plain-text executive summary ────────────────

def build_summary_text(flagged_df: pd.DataFrame,
                       summary_df: pd.DataFrame) -> str:
    """
    Build a multi-line plain-text report from the aggregated data.
    Returns the full text as a string (caller writes it to disk).

    Sections:
        1. Header & run metadata
        2. Overall transaction counts
        3. Reconciliation status breakdown
        4. Risk level breakdown
        5. Financial exposure
        6. Account-level summary table
        7. Top 5 transactions by absolute variance
    """
    today      = date.today().strftime("%Y-%m-%d")
    total_rows = len(flagged_df)
    totals_row = summary_df[summary_df["account_id"] == "TOTAL"].iloc[0]

    W = 62   # report width

    def section(title):
        return f"\n{'─' * W}\n  {title}\n{'─' * W}"

    lines = []

    # ── Header ───────────────────────────────────────────────
    lines.append("=" * W)
    lines.append("  BANK RECONCILIATION AND RISK DETECTION MODEL")
    lines.append("  Executive Summary Report")
    lines.append("=" * W)
    lines.append(f"  Run date   : {today}")
    lines.append(f"  Data period: Q1 2024  (2024-01-01 to 2024-03-31)")
    lines.append(f"  Accounts   : {flagged_df['account_id'].nunique()}")
    lines.append(f"  Prepared by: automated pipeline  (bank-recon-project)")

    # ── Overall counts ────────────────────────────────────────
    lines.append(section("1. TRANSACTION OVERVIEW"))
    disc_count = int(totals_row["discrepancy_count"])
    disc_rate  = totals_row["discrepancy_rate_pct"]
    lines.append(f"  Total transactions reviewed : {total_rows:>6}")
    lines.append(f"  Matched (no discrepancy)    : {int(totals_row['matched_count']):>6}")
    lines.append(f"  Discrepancies identified    : {disc_count:>6}  ({disc_rate:.1f}%)")

    # ── Status breakdown ──────────────────────────────────────
    lines.append(section("2. RECONCILIATION STATUS BREAKDOWN"))
    status_counts = flagged_df["status"].value_counts()
    for status in ["MATCHED", "AMOUNT_MISMATCH", "DATE_MISMATCH",
                   "BANK_ONLY", "SYSTEM_ONLY"]:
        n   = status_counts.get(status, 0)
        pct = n / total_rows * 100
        lines.append(f"  {status:<22} {n:>4}   ({pct:5.1f}%)")

    dup_count = flagged_df["is_duplicate"].sum()
    lines.append(f"\n  Duplicate transaction IDs detected : {dup_count}")

    # ── Risk breakdown ────────────────────────────────────────
    lines.append(section("3. RISK LEVEL BREAKDOWN"))
    risk_counts = flagged_df["risk_level"].value_counts()
    for level, label in [
        ("HIGH",   "Immediate escalation required"),
        ("MEDIUM", "Investigate this cycle"),
        ("LOW",    "Monitor / no urgent action"),
    ]:
        n   = risk_counts.get(level, 0)
        pct = n / total_rows * 100
        lines.append(f"  {level:<8} {n:>4}  ({pct:5.1f}%)   {label}")

    # ── Financial exposure ────────────────────────────────────
    lines.append(section("4. FINANCIAL EXPOSURE"))
    total_var    = flagged_df.loc[flagged_df["status"] != "MATCHED", "variance"]
    gross_exp    = round(total_var.abs().sum(), 2)
    net_exp      = round(total_var.sum(), 2)
    bank_only_v  = round(
        flagged_df.loc[flagged_df["status"] == "BANK_ONLY",   "variance"].sum(), 2)
    sys_only_v   = round(
        flagged_df.loc[flagged_df["status"] == "SYSTEM_ONLY", "variance"].sum(), 2)
    amt_var_v    = round(
        flagged_df.loc[flagged_df["status"] == "AMOUNT_MISMATCH", "variance"].sum(), 2)

    lines.append(f"  Gross variance exposure (|sum|)  : ${gross_exp:>12,.2f}")
    lines.append(f"  Net variance (bank − system)     : ${net_exp:>12,.2f}")
    lines.append(f"    of which — Bank-only exposure  : ${bank_only_v:>12,.2f}")
    lines.append(f"             — System-only exposure: ${sys_only_v:>12,.2f}")
    lines.append(f"             — Amount mismatches   : ${amt_var_v:>12,.2f}")

    # ── Account-level table ───────────────────────────────────
    lines.append(section("5. ACCOUNT SUMMARY"))
    # Build a compact fixed-width table from the summary DataFrame
    # (exclude the TOTAL row here; show it separately at the bottom)
    data_rows = summary_df[summary_df["account_id"] != "TOTAL"]

    hdr = (f"  {'Account':<32} {'Txns':>5} {'Disc':>5} "
           f"{'Disc%':>6} {'Variance $':>12} {'HighRisk':>8}")
    lines.append(hdr)
    lines.append("  " + "-" * (len(hdr) - 2))

    for _, row in data_rows.iterrows():
        name   = str(row["account_name"])[:30]
        lines.append(
            f"  {name:<32} {int(row['total_transactions']):>5} "
            f"{int(row['discrepancy_count']):>5} "
            f"{row['discrepancy_rate_pct']:>5.1f}% "
            f"{row['total_variance_usd']:>12,.2f} "
            f"{row['highest_risk_level']:>8}"
        )

    lines.append("  " + "-" * (len(hdr) - 2))
    tr = summary_df[summary_df["account_id"] == "TOTAL"].iloc[0]
    lines.append(
        f"  {'TOTALS':<32} {int(tr['total_transactions']):>5} "
        f"{int(tr['discrepancy_count']):>5} "
        f"{tr['discrepancy_rate_pct']:>5.1f}% "
        f"{tr['total_variance_usd']:>12,.2f} "
        f"{tr['highest_risk_level']:>8}"
    )

    # ── Top 5 by variance ─────────────────────────────────────
    lines.append(section("6. TOP 5 TRANSACTIONS BY VARIANCE"))
    top5 = (
        flagged_df[flagged_df["status"] != "MATCHED"]
        .assign(abs_var=flagged_df["variance"].abs())
        .nlargest(5, "abs_var")
    )
    t_hdr = (f"  {'TXN ID':<12} {'Account':<28} {'Status':<18} "
             f"{'Variance $':>12} {'Risk':>6}")
    lines.append(t_hdr)
    lines.append("  " + "-" * (len(t_hdr) - 2))
    for _, row in top5.iterrows():
        name = str(row["account_name"])[:26]
        lines.append(
            f"  {row['transaction_id']:<12} {name:<28} "
            f"{row['status']:<18} {row['variance']:>12,.2f} "
            f"{row['risk_level']:>6}"
        )

    lines.append("\n" + "=" * W)
    lines.append("  END OF REPORT")
    lines.append("=" * W + "\n")

    return "\n".join(lines)


# ── Orchestrator ──────────────────────────────────────────────

def run_summary():
    """
    Full summary pipeline:
      load → account aggregation → totals row → text report → save
    Called by main.py Step 4.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load
    flagged_df, accounts_df = load_data()

    # 2. Build per-account summary table
    summary_df = build_account_summary(flagged_df, accounts_df)

    # 3. Append a TOTALS row
    summary_df = append_totals_row(summary_df)

    # 4. Save summary_report.csv
    csv_path = os.path.join(OUTPUT_DIR, "summary_report.csv")
    summary_df.to_csv(csv_path, index=False)
    print(f"  Saved: {os.path.abspath(csv_path)}  ({len(summary_df)} rows incl. totals)")

    # 5. Build and save summary_report.txt
    summary_text = build_summary_text(flagged_df, summary_df)
    txt_path = os.path.join(OUTPUT_DIR, "summary_report.txt")
    with open(txt_path, "w") as f:
        f.write(summary_text)
    print(f"  Saved: {os.path.abspath(txt_path)}")

    return summary_df


# Allow running this file directly for testing
if __name__ == "__main__":
    run_summary()
