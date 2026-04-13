# generate_data.py
#
# This script creates the fake data we need to test the reconciliation
# pipeline. It builds three CSV files that represent what a bank analyst
# would receive at the start of a reconciliation cycle:
#
#   accounts.csv            - the list of customer accounts
#   bank_transactions.csv   - transactions as reported by the bank
#   system_transactions.csv - the same transactions as recorded
#                             by the bank's internal system
#
# To make this realistic and interesting, I deliberately introduced
# four types of data problems that analysts have to catch in real life:
#   - Missing transactions  (some records only exist on one side)
#   - Amount mismatches     (same transaction ID, different amount)
#   - Duplicate transactions(same transaction posted twice)
#   - Date mismatches       (same transaction ID, different date)

import pandas as pd
import numpy as np
import os
import random
from datetime import date, timedelta

# Seed for reproducibility – same data every run
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ── helpers ──────────────────────────────────────────────────

def _random_date(start: date, end: date) -> str:
    """Return a random date string (YYYY-MM-DD) between start and end."""
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def _random_amount() -> float:
    """
    Return a realistic transaction amount.
    Mix of small retail amounts and larger commercial amounts.
    """
    tier = random.random()
    if tier < 0.6:
        # Small retail: $10 – $999
        return round(random.uniform(10, 999), 2)
    elif tier < 0.9:
        # Mid-range: $1 000 – $9 999
        return round(random.uniform(1000, 9999), 2)
    else:
        # Large commercial: $10 000 – $50 000
        return round(random.uniform(10000, 50000), 2)


# ── Step 1: accounts ─────────────────────────────────────────

def generate_accounts() -> pd.DataFrame:
    """
    Build a 10-row master account table.
    Each row represents one customer account held at the bank.
    Writes data/accounts.csv and returns the DataFrame.

    Columns:
        account_id   – unique identifier  (ACC-001 … ACC-010)
        account_name – fictional business or personal name
        account_type – Checking / Savings / Business
        status       – Active / Inactive (one account is inactive to
                       make the data a little more realistic)
    """
    names = [
        "Greenfield Logistics LLC",
        "Sandra Okafor",
        "Blue Horizon Retail Co.",
        "Marcus Tran",
        "Silverline Medical Group",
        "Pinewood Properties Inc.",
        "Yuki Nakamura",
        "Crestview Auto Parts",
        "Elena Vasquez",
        "Northgate Capital Partners",
    ]
    account_types = [
        "Business", "Checking", "Business", "Checking", "Business",
        "Business", "Savings",  "Business", "Savings",  "Business",
    ]
    # Account 7 (ACC-007) is inactive – realistic edge case
    statuses = ["Active"] * 10
    statuses[6] = "Inactive"

    accounts = pd.DataFrame({
        "account_id":   [f"ACC-{str(i).zfill(3)}" for i in range(1, 11)],
        "account_name": names,
        "account_type": account_types,
        "status":       statuses,
    })

    path = os.path.join(DATA_DIR, "accounts.csv")
    accounts.to_csv(path, index=False)
    print(f"    accounts.csv          → {len(accounts)} rows")
    return accounts


# ── Step 2: bank transactions ─────────────────────────────────

def generate_bank_transactions(accounts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Produce 100 base transactions, then inject 5 duplicates to
    represent double-posting errors visible on the bank side.
    Writes data/bank_transactions.csv and returns the DataFrame.

    Columns:
        transaction_id  – unique per original transaction (TXN-0001 …)
        account_id      – FK to accounts.csv
        transaction_date– posting date (YYYY-MM-DD)
        amount          – positive = credit, negative = debit
        transaction_type– Deposit / Withdrawal / Transfer / Fee
        description     – short narrative
        source          – always "BANK" so origin is traceable
    """
    account_ids = accounts_df["account_id"].tolist()
    tx_types    = ["Deposit", "Withdrawal", "Transfer", "Fee"]
    descriptions = {
        "Deposit":    ["ACH Credit", "Wire In", "Check Deposit", "Cash Deposit"],
        "Withdrawal": ["ATM Withdrawal", "Wire Out", "ACH Debit", "Check Paid"],
        "Transfer":   ["Internal Transfer", "Interbank Transfer"],
        "Fee":        ["Monthly Service Fee", "Overdraft Fee", "Wire Fee"],
    }

    START = date(2024, 1, 1)
    END   = date(2024, 3, 31)   # one quarter of data

    rows = []
    for i in range(1, 101):
        tx_type = random.choice(tx_types)
        amount  = _random_amount()
        # Debits (outflows) are negative
        if tx_type in ("Withdrawal", "Fee"):
            amount = -amount

        rows.append({
            "transaction_id":   f"TXN-{str(i).zfill(4)}",
            "account_id":       random.choice(account_ids),
            "transaction_date": _random_date(START, END),
            "amount":           amount,
            "transaction_type": tx_type,
            "description":      random.choice(descriptions[tx_type]),
            "source":           "BANK",
        })

    bank_df = pd.DataFrame(rows)

    # ── Inject duplicates (5 rows) ──────────────────────────
    # Pick 5 random transactions and repeat them. In real life this
    # happens when a batch file is processed twice by mistake.
    duplicate_rows = bank_df.sample(5, random_state=RANDOM_SEED).copy()
    bank_df = pd.concat([bank_df, duplicate_rows], ignore_index=True)
    # Sort by transaction_id so duplicates sit next to each other
    bank_df = bank_df.sort_values("transaction_id").reset_index(drop=True)

    path = os.path.join(DATA_DIR, "bank_transactions.csv")
    bank_df.to_csv(path, index=False)
    print(f"    bank_transactions.csv → {len(bank_df)} rows  "
          f"(100 base + 5 duplicates)")
    return bank_df


# ── Step 3: system transactions ───────────────────────────────

def generate_system_transactions(bank_df: pd.DataFrame) -> pd.DataFrame:
    """
    Start with the 100 unique bank transactions (duplicates removed),
    then apply four types of deliberate data corruption to simulate
    the errors an analyst must find.

    Corruption applied:
        1. Drop 6 rows entirely    → BANK_ONLY discrepancies
        2. Alter amount on 8 rows  → AMOUNT_MISMATCH discrepancies
        3. Shift date on 6 rows    → DATE_MISMATCH discrepancies
        4. Add 4 system-only rows  → SYSTEM_ONLY discrepancies

    Writes data/system_transactions.csv and returns the DataFrame.

    Columns mirror bank_transactions.csv except source = "SYSTEM".
    """
    # Start clean: deduplicate so we work from 100 unique transactions
    system_df = (
        bank_df
        .drop_duplicates(subset="transaction_id", keep="first")
        .copy()
        .reset_index(drop=True)
    )
    system_df["source"] = "SYSTEM"

    # Use a separate RNG so changes are predictable but distinct
    rng = np.random.default_rng(RANDOM_SEED + 1)

    # 1. DROP 6 transactions (system never recorded them)
    drop_idx = rng.choice(system_df.index, size=6, replace=False)
    system_df = system_df.drop(index=drop_idx).reset_index(drop=True)

    # 2. ALTER AMOUNTS on 8 transactions
    #    Add a small % variance to simulate rounding or FX errors
    alter_idx = rng.choice(system_df.index, size=8, replace=False)
    for idx in alter_idx:
        original = system_df.at[idx, "amount"]
        # Vary by ±1% to ±15%
        pct_change = rng.uniform(0.01, 0.15) * random.choice([-1, 1])
        system_df.at[idx, "amount"] = round(original * (1 + pct_change), 2)

    # 3. SHIFT DATES on 6 transactions (±1 to ±5 days)
    date_idx = rng.choice(system_df.index, size=6, replace=False)
    for idx in date_idx:
        original_date = pd.to_datetime(system_df.at[idx, "transaction_date"])
        shift_days    = int(rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]))
        new_date      = original_date + timedelta(days=shift_days)
        system_df.at[idx, "transaction_date"] = new_date.strftime("%Y-%m-%d")

    # 4. ADD 4 system-only transactions (bank never reported them)
    #    These represent entries the system created with no bank counterpart
    account_ids = bank_df["account_id"].unique().tolist()
    START = date(2024, 1, 1)
    END   = date(2024, 3, 31)
    ghost_rows = []
    for i in range(4):
        # Use IDs above TXN-0100 so they can never accidentally match
        ghost_rows.append({
            "transaction_id":   f"TXN-{str(200 + i).zfill(4)}",
            "account_id":       random.choice(account_ids),
            "transaction_date": _random_date(START, END),
            "amount":           _random_amount(),
            "transaction_type": "Transfer",
            "description":      "System Adjustment",
            "source":           "SYSTEM",
        })

    system_df = pd.concat(
        [system_df, pd.DataFrame(ghost_rows)], ignore_index=True
    )
    system_df = system_df.sort_values("transaction_id").reset_index(drop=True)

    path = os.path.join(DATA_DIR, "system_transactions.csv")
    system_df.to_csv(path, index=False)
    print(f"    system_transactions.csv → {len(system_df)} rows  "
          f"(94 from bank − 6 dropped + 4 ghost entries)")
    return system_df


# ── Orchestrator ──────────────────────────────────────────────

def generate_all():
    """
    Run all three generators in the correct dependency order.
    Called by main.py Step 1.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    accounts_df = generate_accounts()
    bank_df     = generate_bank_transactions(accounts_df)
    generate_system_transactions(bank_df)

    print(f"  Data written to: {os.path.abspath(DATA_DIR)}")


# Allow running this file directly for testing
if __name__ == "__main__":
    generate_all()
