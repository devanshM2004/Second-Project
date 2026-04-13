# Bank Reconciliation and Risk Detection Model

A student portfolio project simulating the day-to-day work of an entry-level
**Bank Account Analyst** or **Bank Operations Analyst**.

---

## Business Purpose

Banks maintain two separate records of every transaction:

1. **The bank's external record** – the official ledger sent by the clearing
   house or correspondent bank (`bank_transactions.csv`).
2. **The internal system record** – what the bank's own core-banking software
   captured (`system_transactions.csv`).

These two sources *should* match perfectly. When they don't, it indicates a
potential financial error, processing failure, fraud signal, or compliance
risk. Reconciliation is the process of finding and resolving those gaps.

This project automates that process end-to-end:

- **Generate** realistic synthetic data (with deliberate errors)
- **Reconcile** bank vs. system records
- **Flag** high-risk discrepancies using a scoring model
- **Report** findings in analyst-ready outputs

---

## Project Structure

```
bank-recon-project/
├── data/                        # Input CSVs (created by generate_data.py)
│   ├── accounts.csv
│   ├── bank_transactions.csv
│   └── system_transactions.csv
├── output/                      # Analysis results
│   ├── reconciliation_results.csv
│   ├── risk_flags.csv
│   ├── summary_report.txt
│   └── high_risk_transactions.csv
├── src/
│   ├── generate_data.py         # Step 1 – synthetic data factory
│   ├── reconcile.py             # Step 2 – matching & variance calc
│   ├── flag_risks.py            # Step 3 – rule-based risk scoring
│   └── report.py                # Step 4 – summary & export
├── main.py                      # Runs the full pipeline
├── requirements.txt
└── README.md
```

---

## Data Files

| File | Rows | Description |
|------|------|-------------|
| `accounts.csv` | ~20 | Customer accounts with account type and status |
| `bank_transactions.csv` | ~120 | Transactions as reported by the bank (includes duplicates) |
| `system_transactions.csv` | ~115 | Transactions recorded in the internal system (includes missing/altered rows) |

### Intentional Data Quality Issues

| Issue | Description |
|-------|-------------|
| Missing transactions | Some bank transactions were never recorded in the system, and vice-versa |
| Amount mismatches | Same `transaction_id` but different posted amounts in each source |
| Duplicate transactions | The same `transaction_id` posted twice in one source |
| Date mismatches | Same `transaction_id` but different posting date in each source |

---

## Workflow

```
generate_data.py  →  reconcile.py  →  flag_risks.py  →  report.py
     (data/)             (output/)        (output/)       (output/)
```

### Step 1 – Data Generation (`generate_data.py`)
Creates three CSV files with realistic account and transaction data, then
deliberately injects data quality issues to simulate real-world problems.

### Step 2 – Reconciliation (`reconcile.py`)
Outer-joins bank and system records on `transaction_id`, then classifies
every row as one of:
- `MATCHED` – both sources agree
- `AMOUNT_MISMATCH` – same transaction, different dollar amount
- `DATE_MISMATCH` – same transaction, different posting date
- `BANK_ONLY` – transaction in bank file, missing from system
- `SYSTEM_ONLY` – transaction in system, missing from bank file

### Step 3 – Risk Flagging (`flag_risks.py`)
Applies a simple rule-based scoring model to each discrepancy and assigns a
`risk_level` of `HIGH`, `MEDIUM`, or `LOW`.

### Step 4 – Reporting (`report.py`)
Produces a plain-text executive summary and a filtered CSV of high-risk items.

---

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline
python main.py
```

All outputs are saved to the `output/` folder.

---

## Sample Output (summary_report.txt)

```
========================================
  BANK RECONCILIATION SUMMARY REPORT
========================================
Run Date : 2026-04-13
...
RECONCILIATION STATUS
  MATCHED          :  89  (74%)
  AMOUNT_MISMATCH  :  10  ( 8%)
  DATE_MISMATCH    :   8  ( 7%)
  BANK_ONLY        :   9  ( 8%)
  SYSTEM_ONLY      :   4  ( 3%)

RISK BREAKDOWN
  HIGH   : 15
  MEDIUM : 18
  LOW    : 87

TOTAL VARIANCE EXPOSURE : $24,310.50
...
```

---

## Skills Demonstrated

- **Data wrangling** with pandas (merge, groupby, apply, value_counts)
- **Business logic** encoding (reconciliation rules, risk scoring)
- **Data quality** analysis and variance calculation
- **Report generation** from structured data
- **Project organisation** for a multi-script Python workflow

---

## Interview Talking Points

- "I simulated a real bank reconciliation cycle from raw data through risk
  reporting, which mirrors what account analysts do in daily BAU operations."
- "I intentionally injected data quality issues—missing records, amount
  mismatches, duplicates—to practice the kinds of problems analysts face."
- "The risk scoring model uses a transparent, rule-based approach that a
  compliance team could audit and adjust without touching code."
