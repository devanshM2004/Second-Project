# Emerging Risk Identification and Monitoring Framework

> A Python portfolio project simulating the work of a Strategy &
> Emerging Risk team at a large financial institution.

---

## What Is Emerging Risk?

Every major financial institution has a team whose job is to look around
corners — to spot threats before they become crises. These threats are
called **emerging risks**: risks that are new, fast-evolving, or not yet
fully captured by traditional risk management frameworks.

Examples of emerging risks a bank would monitor today:

- A ransomware attack that could lock down core banking systems overnight
- Generative AI tools being used across the business without governance guardrails
- Climate change gradually eroding the value of mortgage collateral
- New regulations that haven't been finalised yet but will reshape operations

Unlike well-established risks (e.g. credit default, which banks have managed
for decades), emerging risks are harder to quantify. A strategy and emerging
risk team must identify them early, score them systematically, and ensure
the right people are paying attention — before the risk materialises.

This project replicates that process end-to-end using Python.

---

## Project Structure

```
emerging-risk-project/
├── data/
│   └── risk_register_raw.csv       ← synthetic input / scored register
├── output/
│   ├── risk_register.csv           ← full scored register (30 rows)
│   ├── executive_summary.csv       ← Escalate + Watchlist items only
│   ├── top_5_risks.csv             ← highest residual-risk items
│   ├── risk_counts_by_category.csv ← aggregated view by category
│   └── risk_heatmap.png            ← likelihood × impact heat map
├── src/
│   ├── data_generator.py           ← builds the synthetic risk register
│   ├── scoring.py                  ← applies all scoring logic
│   └── reporting.py                ← generates CSVs and the heat map
├── main.py                         ← runs the full pipeline
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

---

## How the Scoring Works

Each risk is scored across three raw dimensions (all rated 1–5):

| Field | What It Measures |
|---|---|
| `likelihood_score` | How probable is this risk event? (1=Rare → 5=Almost Certain) |
| `impact_score` | How severe would the damage be? (1=Negligible → 5=Critical) |
| `velocity_score` | How fast could it escalate once it starts? (1=Slow → 5=Immediate) |
| `control_effectiveness` | How well do existing controls reduce this risk? (0.0–1.0 decimal) |

Those inputs feed three derived scores:

### 1. Inherent Risk
> **Formula:** `likelihood × impact`  
> **Scale:** 1–25

This is the **raw exposure** — how bad the risk would be if we had no
controls at all. A score of 20 (e.g. likelihood=4, impact=5) means the
event is likely and the consequences would be severe.

### 2. Residual Risk
> **Formula:** `inherent_risk × (1 − control_effectiveness)`  
> **Scale:** roughly 3–12 in this portfolio

This is the **exposure that remains after controls do their job**.
Control effectiveness acts as a discount factor:

- `control_effectiveness = 0.60` means controls reduce exposure by 60%,
  leaving 40% of the inherent risk still present.
- `control_effectiveness = 0.30` means controls are weak — 70% of the
  raw exposure is still live.

**Example:**  
Ransomware Attack — inherent risk = 20, control effectiveness = 55%  
→ residual risk = 20 × (1 − 0.55) = **9.0 (Escalate)**

### 3. Risk Status
The residual score is translated into an actionable triage label:

| Status | Residual Score | Meaning |
|---|---|---|
| **Escalate** | ≥ 9.0 | Needs immediate senior leadership attention |
| **Watchlist** | ≥ 6.0 | Elevated — review monthly, ready to escalate |
| **Monitor** | < 6.0 | Manageable — standard quarterly review cycle |

### 4. Priority Flag
A boolean flag (`True`/`False`) that marks risks requiring **urgent
attention**. Set to `True` when:
- `residual_risk ≥ 9` (Escalate tier), **AND**
- `trend_direction == "Increasing"` (the situation is actively worsening)

A priority-flagged risk is the highest-urgency item in the register — high
residual exposure and a deteriorating trend means leadership needs to act now.

---

## What the Outputs Show

### `output/risk_register.csv`
The complete 30-row register with every field and all four derived scores.
This is the master document a risk team would maintain and update monthly.

### `output/executive_summary.csv`
A filtered view containing only **Escalate** and **Watchlist** items,
sorted by residual risk. This is what gets presented at a Risk Committee
or board-level meeting — leadership doesn't need to see the full register,
just the items requiring attention.

### `output/top_5_risks.csv`
The five risks with the highest residual score. Useful for a one-page
summary or a slide in a board pack showing the firm's most pressing
emerging exposures.

### `output/risk_counts_by_category.csv`
An aggregated view showing, for each risk category:
- total number of risks
- how many are Escalate / Watchlist / Monitor
- average residual score
- number of priority-flagged items

This helps senior management see which *areas* (e.g. Cybersecurity,
Climate/ESG, Geopolitical) are most exposed at a portfolio level.

### `output/risk_heatmap.png`
A **Likelihood × Impact scatter chart** — the classic tool used in risk
management to visualise the full portfolio at a glance.

- **x-axis:** Likelihood (1=Rare → 5=Almost Certain)
- **y-axis:** Impact (1=Negligible → 5=Critical)
- **Colour:** Green=Monitor, Orange=Watchlist, Red=Escalate
- **Star marker:** Priority-flagged items (high residual + increasing trend)

The top-right quadrant is the "danger zone" — risks that are both likely
and catastrophic. Items clustering there are your Escalate cases and the
first things a risk committee will ask about.

---

## How This Simulates Real Strategy and Emerging Risk Work

This project mirrors the actual workflow of an emerging risk team at a
major bank or insurance company:

| Step | Real-World Activity | This Project |
|---|---|---|
| **Identify** | Horizon scanning, internal nominations, regulatory bulletins | 30 hand-crafted synthetic risks across 11 categories |
| **Score** | Risk committees score likelihood, impact, velocity, controls | `scoring.py` applies the inherent/residual model |
| **Triage** | Risks classified into action tiers for governance routing | `risk_status` labels (Escalate / Watchlist / Monitor) |
| **Prioritise** | Items with worsening trends flagged for urgent escalation | `priority_flag` column |
| **Report** | Committee packs, board updates, category roll-ups | Executive summary CSV, top-5, category counts |
| **Visualise** | Heat maps presented at Risk Committee and board level | `risk_heatmap.png` |

The **risk categories** in this dataset reflect what a large financial
institution would actually monitor:

| Category | Why It's Emerging Right Now |
|---|---|
| Cybersecurity | Ransomware, AI-powered phishing, quantum computing threats |
| Regulatory / Compliance | Basel IV, digital assets, CFPB rulemaking |
| Climate / ESG | Physical risk to collateral, carbon pricing, greenwashing enforcement |
| Geopolitical | US–China trade war, sanctions evasion, energy market shocks |
| Technology / AI | Model bias, legacy migration failure, GenAI governance gaps |
| Market Risk | CRE collapse, interest rate volatility, deposit outflows |
| Operational Risk | Cloud outages, talent attrition, synthetic identity fraud |
| Credit Risk | Consumer deterioration, leveraged loans, EM sovereign contagion |
| Third-Party / Vendor | Critical vendor insolvency, data localisation laws |
| Strategic Risk | Fintech disintermediation, GenAI without governance |
| Conduct / Legal | Mis-selling, insider data theft |

---

## Interview Talking Points

**On the dataset:**
> "I designed 30 realistic emerging risks that mirror what a bank's strategy
> team would actually track — covering cyber, climate, geopolitical, and
> regulatory themes that are live issues in financial services today."

**On the scoring model:**
> "The inherent vs. residual risk distinction is fundamental to how risk
> professionals think. A risk might look severe on paper, but if controls
> are strong, the residual exposure can be quite manageable. Control
> effectiveness is the key lever."

**On the heat map:**
> "The heat map gives leadership a portfolio view in seconds. Top-right means
> high likelihood and high impact — those are your Escalate items, the ones
> that need a mitigation plan immediately. Bottom-left is your Monitor bucket."

**On velocity:**
> "Velocity is what separates emerging risk thinking from traditional risk
> management. A slow-moving regulatory change and a sudden cyberattack might
> have the same inherent score, but they require very different response
> timelines."

**On the priority flag:**
> "The flag catches the intersection of two bad things: the residual exposure
> is already high, AND the trajectory is getting worse. That combination is
> what a Chief Risk Officer needs to see at the top of the board pack."
