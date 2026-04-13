# ============================================================
# src/generate_data.py
# ============================================================
# PURPOSE:
#   Create three synthetic CSV files that mimic what a bank
#   analyst would receive at the start of a reconciliation cycle.
#
#   accounts.csv          – master list of customer accounts
#   bank_transactions.csv – transactions as reported by the bank
#   system_transactions.csv – transactions recorded in the
#                             bank's internal core-banking system
#
# INTENTIONAL DATA QUALITY ISSUES INTRODUCED:
#   - Missing transactions  : some bank records have no matching
#                             system record and vice-versa
#   - Amount mismatches     : a few records share a transaction_id
#                             but differ in posted amount
#   - Duplicate transactions: the same transaction appears twice
#                             in one of the data sources
#   - Date mismatches       : same transaction_id but different
#                             posting date in each source
# ============================================================

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


def generate_accounts():
    """
    Build a small master account table.
    Each row = one customer account.
    Returns a DataFrame and writes accounts.csv to data/.
    """
    # TODO: implement account generation
    pass


def generate_bank_transactions(accounts_df):
    """
    Simulate the transaction file received from the external bank.
    Introduces duplicates so the analyst must catch them.
    Returns a DataFrame and writes bank_transactions.csv to data/.
    """
    # TODO: implement bank transaction generation
    pass


def generate_system_transactions(bank_df):
    """
    Simulate what the internal core-banking system recorded.
    Derived from the bank file, then deliberately corrupted with:
      - removed rows  (missing transactions)
      - altered amounts (amount mismatches)
      - shifted dates  (date mismatches)
    Returns a DataFrame and writes system_transactions.csv to data/.
    """
    # TODO: implement system transaction generation
    pass


def generate_all():
    """
    Orchestrate all three generators in the correct order.
    Called by main.py Step 1.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    accounts_df = generate_accounts()
    bank_df = generate_bank_transactions(accounts_df)
    generate_system_transactions(bank_df)

    print(f"  Data written to: {os.path.abspath(DATA_DIR)}")
