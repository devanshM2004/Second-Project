# Payroll Reconciliation and Variance Analysis Model

This project is a finance and operations portfolio piece built to demonstrate entry-level skills relevant to payroll operations, financial data handling, reconciliation, variance analysis, and internal reporting.

## Project Goal
The goal of this project is to simulate a payroll review workflow using sample employee compensation data. The model calculates gross pay, deductions, net pay, payroll expense summaries, and period-over-period payroll variances. It also flags unusual changes that would normally require review.

## Why this project matters
This project is relevant to entry-level roles in payroll, banking operations, financial operations, and data-driven support roles. It shows the ability to:
- work with structured financial data
- clean and validate records
- calculate payroll metrics
- identify anomalies and variances
- summarize results for internal review
- use Git and GitHub to manage a project

## Tools Used
- Python
- pandas
- pathlib
- CSV files
- Git / GitHub
- Windows PowerShell for local execution

## Project Structure
```text
Second-Project/
  README.md
  data/
    sample_payroll_data.csv
  scripts/
    calculate_payroll.py
  outputs/
    payroll_summary.csv
    payroll_variance_report.csv
```

## Inputs
The input file contains sample payroll data with the following fields:
- employee_id
- employee_name
- department
- pay_period
- hourly_rate
- regular_hours
- overtime_hours
- benefit_deduction
- other_deduction
- prior_period_net_pay

## Calculations
The script calculates:
- regular pay
- overtime pay
- gross pay
- estimated tax withholding
- total deductions
- net pay
- variance vs prior period net pay
- variance percentage
- review flag for unusual payroll swings

## Review Flag Logic
A payroll record is flagged for review when the period-over-period net pay variance exceeds 10.00% in absolute value.

## Output Files
### payroll_summary.csv
Contains employee-level payroll results for the pay period.

### payroll_variance_report.csv
Contains only the employees flagged for payroll review based on unusual net pay changes.

## How to Run
From the project folder, run:

```powershell
python scripts/calculate_payroll.py
```

## Example Business Use
A payroll assistant or operations analyst could use this model to:
- review employee payroll before final submission
- identify unusual changes in pay
- support reconciliation of payroll expense
- prepare summary outputs for accounting or management review

## Resume-Ready Description
Built a payroll reconciliation and variance analysis model using Python and sample compensation data to calculate gross-to-net pay, identify unusual payroll swings, and generate review-ready payroll summaries for financial operations support.
