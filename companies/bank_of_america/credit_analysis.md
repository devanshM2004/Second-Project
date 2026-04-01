# Bank of America – Credit Risk Analysis Framework

## Overview

This document outlines the credit risk framework used by lenders like Bank of America when evaluating loan applications. Credit risk is the probability that a borrower will fail to meet their repayment obligations, resulting in a financial loss for the lender.

Lenders manage this risk through structured analysis, risk-based pricing, and loan structuring — not simply by approving or rejecting applications.

---

## The 5 Cs of Credit

The industry-standard framework for evaluating borrower risk is the **5 Cs of Credit**: Character, Capacity, Capital, Collateral, and Conditions.

### 1. Character
*Does the borrower have a history of honoring financial commitments?*

Character is assessed through the borrower's credit profile:

- **FICO credit score** (range: 300–850):
  - 760+: Prime — low risk
  - 680–759: Near-prime — moderate risk
  - 580–679: Subprime — elevated risk
  - Below 580: Deep subprime — high risk
- Payment history on existing loans and credit cards
- Delinquencies, collections, charge-offs, or bankruptcies
- Length of credit history and number of open accounts

Character is the most behavioral signal in the analysis — past repayment behavior is the strongest predictor of future default.

### 2. Capacity
*Can the borrower generate enough income to repay the loan?*

Capacity is the most quantitative dimension of credit analysis. The primary metric for consumer lending is **Debt-to-Income (DTI) ratio**:

```
DTI = Total Monthly Debt Payments / Gross Monthly Income
```

Industry thresholds:
- DTI ≤ 36%: Strong — comfortable repayment margin
- DTI 37–43%: Acceptable — most lenders' upper limit
- DTI > 43%: High risk — often triggers automatic decline

For commercial and business borrowers, lenders use **Debt Service Coverage Ratio (DSCR)**:

```
DSCR = Net Operating Income / Total Annual Debt Service
```

- DSCR ≥ 1.25x: Acceptable minimum for most commercial loans
- DSCR = 1.0x: Break-even — no buffer for unexpected costs
- DSCR < 1.0x: Borrower cannot service debt from operations — decline

### 3. Capital
*Does the borrower have savings or assets to fall back on if income is disrupted?*

Capital acts as a cushion against default:

- Cash savings and liquid reserves
- Investment or retirement account balances
- Down payment contributed (signals commitment and reduces lender exposure)

Rule of thumb: **2–6 months of loan payments in liquid reserves** is a positive signal. Thin reserves elevate risk even when current income looks adequate.

### 4. Collateral
*Is there an asset securing the loan that the lender can recover in case of default?*

Collateral reduces **loss-given-default (LGD)** — the lender's exposure if the borrower stops paying.

Examples:
- Mortgage: secured by real estate
- Auto loan: secured by the vehicle
- Personal loan: unsecured — no collateral; lender bears full loss in default

For secured loans, lenders calculate **Loan-to-Value (LTV)**:

```
LTV = Loan Amount / Appraised Value of Collateral
```

- LTV ≤ 80%: Low risk — significant equity cushion
- LTV 81–95%: Moderate risk
- LTV > 95%: High risk — limited recovery if collateral value drops

Unsecured loans compensate for the absence of collateral through higher interest rates.

### 5. Conditions
*What external factors could affect the borrower's ability to repay?*

Conditions reflect the broader environment:

- **Interest rate environment**: Rising rates increase floating-rate debt burden
- **Economic cycle**: Recessions drive unemployment and default rates higher
- **Industry risk**: Borrowers in cyclical industries (retail, hospitality) carry more volatility
- **Loan purpose**: Productive uses (home improvement, business investment) are viewed more favorably than discretionary consumption

Even a strong borrower on paper can become risky under adverse economic conditions.

---

## Lending Decision Framework

Once the 5 Cs are assessed, a lender typically follows this structured process:

1. Collect and verify borrower financial data (income, tax returns, bank statements)
2. Pull credit report and FICO score
3. Calculate key ratios: DTI, DSCR (if applicable), LTV (if secured)
4. Assign a risk rating (e.g., Low / Moderate / High)
5. Determine credit decision: Approve, Approve with Conditions, or Decline
6. If approved: set interest rate and loan terms based on risk level
7. Document the credit rationale (credit memo)

---

## Key Ratios Reference

| Metric | Formula | Healthy Threshold |
|---|---|---|
| Debt-to-Income (DTI) | Monthly debt payments / Gross monthly income | ≤ 43% |
| Debt Service Coverage (DSCR) | Net operating income / Annual debt service | ≥ 1.25x |
| Loan-to-Value (LTV) | Loan amount / Asset value | ≤ 80% |

---

## Key Takeaways for Credit Risk Roles

- **Cash flow matters more than income** — a high earner with high fixed obligations may be riskier than a moderate earner with low debt
- **DTI is the primary capacity metric** in consumer underwriting; learn to calculate it quickly
- **Credit scores influence rate, not just approval** — near-prime borrowers pay higher rates to compensate lenders for elevated default probability
- **Collateral reduces LGD, not probability of default** — it limits how much the lender loses, not whether the borrower defaults
- **Risk is managed through pricing and structure** — adjusting rates, terms, and loan amounts is as important as the approve/decline decision
- **The 5 Cs provide a consistent framework** for defending credit decisions to credit committees and regulators

---

## Why I Built This

I built this framework to develop a practical understanding of how banks evaluate and price credit risk. This reflects the analytical approach used in entry-level credit analyst, underwriting, and commercial banking roles, and is intended to demonstrate that I can think through lending decisions in a structured, metrics-driven way.
