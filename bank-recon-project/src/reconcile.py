# reconcile.py
#
# This is the core of the project. It loads the bank file and the
# system file, joins them together, and figures out where they disagree.
#
# Each transaction gets one of five status labels:
#   MATCHED         - both sources agree (amount and date match)
#   AMOUNT_MISMATCH - same transaction ID but different dollar amount
#   DATE_MISMATCH   - same transaction ID but different posting date
#   BANK_ONLY       - bank recorded it but the system never did
#   SYSTEM_ONLY     - system recorded it but the bank never reported it
#
# I also check for duplicate transaction IDs before the merge so they
# don't create false mismatches, and flag them in their own column.
#
# Outputs:
#   output/reconciled_transactions.csv  - every transaction with its status
#   output/discrepancy_report.csv       - just the rows that need attention

import pandas as pd
import os

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


# ── Step 1: load ──────────────────────────────────────────────

def load_data():
    """
    Read the three source CSVs from data/.
    Returns (bank_df, system_df, accounts_df) as DataFrames.
    Raises FileNotFoundError with a helpful message if any file
    is missing (i.e. generate_data.py hasn't been run yet).
    """
    paths = {
        "bank":     os.path.join(DATA_DIR, "bank_transactions.csv"),
        "system":   os.path.join(DATA_DIR, "system_transactions.csv"),
        "accounts": os.path.join(DATA_DIR, "accounts.csv"),
    }

    for label, path in paths.items():
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing {label} file: {path}\n"
                "Run `python src/generate_data.py` first."
            )

    bank_df     = pd.read_csv(paths["bank"],     dtype=str)
    system_df   = pd.read_csv(paths["system"],   dtype=str)
    accounts_df = pd.read_csv(paths["accounts"], dtype=str)

    # Convert amount to float after loading as str (avoids mixed-type issues)
    bank_df["amount"]   = bank_df["amount"].astype(float)
    system_df["amount"] = system_df["amount"].astype(float)

    print(f"  Loaded {len(bank_df)} bank rows, "
          f"{len(system_df)} system rows, "
          f"{len(accounts_df)} accounts")

    return bank_df, system_df, accounts_df


# ── Step 2: detect duplicates ─────────────────────────────────

def flag_duplicates(bank_df: pd.DataFrame, system_df: pd.DataFrame):
    """
    Find transaction_ids that appear more than once in either source.
    Returns two sets:
        bank_dupe_ids   – IDs duplicated in the bank file
        system_dupe_ids – IDs duplicated in the system file

    Duplicates are removed from the DataFrames before merging
    (keeping the first occurrence) so they don't create false
    AMOUNT_MISMATCH or DATE_MISMATCH entries.
    The caller stamps the is_duplicate column using the sets.
    """
    # A transaction_id is a duplicate if it appears more than once
    bank_dupe_ids   = set(
        bank_df[bank_df.duplicated("transaction_id", keep=False)]["transaction_id"]
    )
    system_dupe_ids = set(
        system_df[system_df.duplicated("transaction_id", keep=False)]["transaction_id"]
    )

    dupe_count = len(bank_dupe_ids) + len(system_dupe_ids)
    print(f"  Duplicates found — bank: {len(bank_dupe_ids)}, "
          f"system: {len(system_dupe_ids)}  ({dupe_count} total IDs)")

    # Deduplicate: keep first occurrence in each source
    bank_clean   = bank_df.drop_duplicates("transaction_id", keep="first").copy()
    system_clean = system_df.drop_duplicates("transaction_id", keep="first").copy()

    return bank_clean, system_clean, bank_dupe_ids, system_dupe_ids


# ── Step 3: merge ─────────────────────────────────────────────

def merge_transactions(bank_df: pd.DataFrame, system_df: pd.DataFrame) -> pd.DataFrame:
    """
    Outer-join the deduplicated bank and system DataFrames on
    transaction_id.

    Columns from each source get a _bank / _sys suffix so
    there's no ambiguity during classification:
        amount_bank, amount_sys
        transaction_date_bank, transaction_date_sys
        account_id_bank, account_id_sys
        transaction_type_bank, transaction_type_sys
        description_bank, description_sys

    Rows present in only one source will have NaN in the other
    source's columns — that's how BANK_ONLY / SYSTEM_ONLY is detected.
    """
    merged = pd.merge(
        bank_df,
        system_df,
        on="transaction_id",
        how="outer",
        suffixes=("_bank", "_sys"),
    )
    return merged


# ── Step 4: classify ──────────────────────────────────────────

def classify_status(merged_df: pd.DataFrame,
                    bank_dupe_ids: set,
                    system_dupe_ids: set) -> pd.DataFrame:
    """
    Assign a status and calculate variance for every row.

    Status logic (applied in priority order):
        1. BANK_ONLY    – amount_sys is NaN  (no system record)
        2. SYSTEM_ONLY  – amount_bank is NaN (no bank record)
        3. AMOUNT_MISMATCH – both present, amounts differ
        4. DATE_MISMATCH   – both present, dates differ
        5. MATCHED         – everything agrees

    variance = bank_amount − system_amount
        Positive → bank recorded more than system (potential overcharge)
        Negative → system recorded more than bank (potential phantom credit)
        0 / NaN  → matched or one-sided record

    is_duplicate = True when the transaction_id appeared more than
    once in either source file.
    """
    statuses  = []
    variances = []

    for _, row in merged_df.iterrows():
        bank_missing   = pd.isna(row["amount_bank"])
        system_missing = pd.isna(row["amount_sys"])

        if bank_missing and system_missing:
            # Shouldn't happen after an outer merge, but guard anyway
            statuses.append("UNKNOWN")
            variances.append(None)

        elif system_missing:
            # Transaction exists in bank file but not in the system
            statuses.append("BANK_ONLY")
            variances.append(row["amount_bank"])   # full amount is unreconciled

        elif bank_missing:
            # Transaction exists in system but was never reported by the bank
            statuses.append("SYSTEM_ONLY")
            variances.append(-row["amount_sys"])   # negative: system shows more

        else:
            # Both sources have the record – check for field-level differences
            variance = round(row["amount_bank"] - row["amount_sys"], 2)

            if row["amount_bank"] != row["amount_sys"]:
                statuses.append("AMOUNT_MISMATCH")
            elif row["transaction_date_bank"] != row["transaction_date_sys"]:
                statuses.append("DATE_MISMATCH")
            else:
                statuses.append("MATCHED")

            variances.append(variance)

    merged_df = merged_df.copy()
    merged_df["status"]   = statuses
    merged_df["variance"] = variances

    # Flag any transaction_id that was a duplicate in either source
    all_dupe_ids = bank_dupe_ids | system_dupe_ids
    merged_df["is_duplicate"] = merged_df["transaction_id"].isin(all_dupe_ids)

    return merged_df


# ── Step 5: shape the output columns ─────────────────────────

def build_output(merged_df: pd.DataFrame, accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Select and rename columns into a clean, analyst-friendly layout.
    Also join the account_name from accounts.csv for readability.

    Final column order:
        transaction_id, account_id, account_name,
        bank_date, sys_date,
        bank_amount, sys_amount, variance,
        transaction_type, description,
        status, is_duplicate
    """
    # Prefer bank-side account_id; fall back to system-side for SYSTEM_ONLY rows
    merged_df["account_id"] = merged_df["account_id_bank"].fillna(
        merged_df["account_id_sys"]
    )

    # Same for transaction_type and description
    merged_df["transaction_type"] = merged_df["transaction_type_bank"].fillna(
        merged_df["transaction_type_sys"]
    )
    merged_df["description"] = merged_df["description_bank"].fillna(
        merged_df["description_sys"]
    )

    # Join account name for human-readable output
    output = merged_df.merge(
        accounts_df[["account_id", "account_name"]],
        on="account_id",
        how="left",
    )

    # Select and rename to the final clean set of columns
    output = output[[
        "transaction_id",
        "account_id",
        "account_name",
        "transaction_date_bank",
        "transaction_date_sys",
        "amount_bank",
        "amount_sys",
        "variance",
        "transaction_type",
        "description",
        "status",
        "is_duplicate",
    ]].rename(columns={
        "transaction_date_bank": "bank_date",
        "transaction_date_sys":  "sys_date",
        "amount_bank":           "bank_amount",
        "amount_sys":            "sys_amount",
    })

    # Sort: discrepancies first, then matched; within each group by transaction_id
    status_order = {
        "BANK_ONLY":       0,
        "SYSTEM_ONLY":     1,
        "AMOUNT_MISMATCH": 2,
        "DATE_MISMATCH":   3,
        "MATCHED":         4,
    }
    output["_sort"] = output["status"].map(status_order)
    output = output.sort_values(["_sort", "transaction_id"]).drop(columns="_sort")
    output = output.reset_index(drop=True)

    return output


# ── Orchestrator ──────────────────────────────────────────────

def run_reconciliation():
    """
    Full reconciliation pipeline:
      load → detect duplicates → merge → classify → shape → save
    Called by main.py Step 2.

    Saves two files:
        output/reconciled_transactions.csv  – all records with status
        output/discrepancy_report.csv       – non-MATCHED records only
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Load
    bank_df, system_df, accounts_df = load_data()

    # 2. Detect & remove duplicates (keep originals for classification)
    bank_clean, system_clean, bank_dupe_ids, system_dupe_ids = flag_duplicates(
        bank_df, system_df
    )

    # 3. Merge on transaction_id (outer join)
    merged_df = merge_transactions(bank_clean, system_clean)

    # 4. Classify each row
    classified_df = classify_status(merged_df, bank_dupe_ids, system_dupe_ids)

    # 5. Shape into clean output columns
    results_df = build_output(classified_df, accounts_df)

    # ── Save reconciled_transactions.csv ──────────────────────
    recon_path = os.path.join(OUTPUT_DIR, "reconciled_transactions.csv")
    results_df.to_csv(recon_path, index=False)
    print(f"  Saved: {os.path.abspath(recon_path)}  ({len(results_df)} rows)")

    # ── Save discrepancy_report.csv ───────────────────────────
    discrepancies_df = results_df[results_df["status"] != "MATCHED"].copy()
    disc_path = os.path.join(OUTPUT_DIR, "discrepancy_report.csv")
    discrepancies_df.to_csv(disc_path, index=False)
    print(f"  Saved: {os.path.abspath(disc_path)}  ({len(discrepancies_df)} discrepancies)")

    # ── Terminal status breakdown ─────────────────────────────
    print("\n  Status breakdown:")
    counts = results_df["status"].value_counts()
    total  = len(results_df)
    for status in ["MATCHED", "AMOUNT_MISMATCH", "DATE_MISMATCH",
                   "BANK_ONLY", "SYSTEM_ONLY"]:
        n = counts.get(status, 0)
        print(f"    {status:<20} {n:>3}  ({n/total*100:.1f}%)")

    return results_df


# Allow running this file directly for testing
if __name__ == "__main__":
    run_reconciliation()
