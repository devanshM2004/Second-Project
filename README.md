# Emerging Risk Identification and Monitoring Framework

> A Python portfolio project simulating the strategy and emerging risk
> function at a large financial institution.

---

## What Is Emerging Risk?

Emerging risks are threats that are new, fast-moving, or not yet fully
captured by traditional risk management frameworks. Unlike well-understood
risks such as credit default or interest rate movements — which banks have
managed for decades — emerging risks require a different discipline: one
built around early identification, systematic scoring, and continuous
monitoring rather than purely quantitative modelling.

Every major bank, insurer, and asset manager maintains a team responsible
for this work. Their job is to look around corners: to spot a geopolitical
shift, a technology threat, or a regulatory change before it becomes a
crisis, and to ensure the right people are paying attention in time to act.

This project replicates that workflow end-to-end — from building a risk
register, to scoring and triaging risks, to producing the reports and
visualisations that land in front of senior leadership.

---

## Project Structure

```
/
├── README.md               ← you are here
├── requirements.txt        ← Python dependencies
├── main.py                 ← runs the full pipeline
├── data/
│   └── risk_register_raw.csv    ← synthetic scored register (written on run)
├── output/
│   ├── risk_register.csv        ← full 30-row scored register
│   ├── executive_summary.csv    ← Escalate + Watchlist items for leadership
│   ├── top_5_risks.csv          ← five highest residual-risk items
│   ├── risk_counts_by_category.csv  ← aggregated view by risk category
│   └── risk_heatmap.png         ← likelihood × impact heat map chart
└── src/
    ├── data_generator.py   ← builds the synthetic risk register (30 risks)
    ├── scoring.py          ← inherent risk, residual risk, status, priority flag
    └── reporting.py        ← generates all CSVs and the heat map
```

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

All output files are written to `output/`.

---

## The Data

The project uses a synthetic dataset of **30 emerging risks** designed to
reflect what a large financial institution's strategy team would actually
monitor. Each risk record contains 15 fields:

| Field | Description |
|---|---|
| `risk_id` | Unique identifier (ER-001 to ER-030) |
| `risk_name` | Short name for the risk |
| `risk_category` | One of 11 categories (see below) |
| `business_unit` | The part of the firm most exposed |
| `description` | Plain-language explanation of the threat |
| `likelihood_score` | How probable is the risk event? (1–5) |
| `impact_score` | How severe would the damage be? (1–5) |
| `velocity_score` | How fast could it escalate once triggered? (1–5) — used in inherent risk scoring |
| `control_effectiveness` | How well do existing controls reduce exposure? (0.0–1.0) — used in residual risk scoring |
| `regulatory_attention` | Level of regulator focus: High / Medium / Low — used to sort the executive summary |
| `trend_direction` | Is the risk Increasing / Stable / Decreasing? |
| `owner` | The senior executive accountable for this risk |
| `mitigation_status` | Not Started / In Progress / Completed |
| `last_review_date` | Date of most recent formal review |
| `next_review_date` | Scheduled next review date |

**Risk categories covered:**

| Category | Example Risk |
|---|---|
| Cybersecurity | Ransomware attack on core banking systems |
| Regulatory / Compliance | Basel IV capital requirements |
| Climate / ESG | Physical climate risk in the mortgage portfolio |
| Geopolitical | US–China trade war escalation |
| Technology / AI | GenAI adoption without a governance framework |
| Market Risk | Commercial real estate valuation collapse |
| Operational Risk | Critical cloud provider outage |
| Credit Risk | Consumer credit deterioration from stagflation |
| Third-Party / Vendor | Critical payment-rail vendor insolvency |
| Strategic Risk | Fintech disintermediation of retail deposits |
| Conduct / Legal | Mis-selling risk in structured products |

---

## How the Scoring Works

### Inherent Risk
> `(likelihood_score × impact_score) + velocity_score` — scale: 3 to 30

The raw exposure before any controls are applied. Three fields contribute:

- **Likelihood × Impact** captures severity — how probable the event is multiplied
  by how damaging it would be (scale 1–25)
- **Velocity** is added as an urgency premium — fast-moving threats leave
  less time for controls to activate, so they score higher (adds 1–5)

Why add rather than multiply? Multiplying by velocity would unfairly penalise
slow-moving but existentially severe risks (climate change, Basel IV). Adding
keeps slow-burn threats visible while still rewarding fast-mover urgency.

**Example — Ransomware Attack** (likelihood=4, impact=5, velocity=5):
- Inherent risk = (4 × 5) + 5 = **25**

**Example — Basel IV** (likelihood=5, impact=4, velocity=2):
- Inherent risk = (5 × 4) + 2 = **22** — still high despite slow velocity

### Residual Risk
> `inherent_risk × (1 − control_effectiveness)` — scale: ~3 to 14

The exposure that remains **after** existing controls do their job.
`control_effectiveness` acts as a discount factor:

- `0.60` → controls absorb 60% of the risk; 40% remains
- `0.30` → weak controls; 70% of raw exposure is still live

**Continuing the Ransomware example:**
- Inherent risk = 25, control effectiveness = 0.55
- Residual risk = 25 × (1 − 0.55) = **11.25 → Escalate**

### Risk Status
Residual risk is translated into a triage label for governance routing.
Thresholds are calibrated to the residual range produced by this portfolio
(approximately 3–14):

| Status | Residual Score | Action Required |
|---|---|---|
| **Escalate** | ≥ 11 | Immediate senior leadership attention; mitigation plan required |
| **Watchlist** | ≥ 7 | Review monthly; escalation criteria defined |
| **Monitor** | < 7 | Standard quarterly review; no immediate action needed |

### Priority Flag
A `True/False` flag that marks the highest-urgency items — those where
residual exposure is already in the Escalate tier **and** the trend is
actively getting worse:

- `residual_risk ≥ 11` (Escalate tier), **AND**
- `trend_direction == "Increasing"`

Priority-flagged risks are what a Chief Risk Officer puts at the top of a
board pack. They represent the intersection of two bad signals: the exposure
is high despite controls, and the trajectory is heading in the wrong direction.

### Regulatory Attention in Outputs
`regulatory_attention` (High / Medium / Low) does not affect the numeric
score — it reflects external pressure from regulators rather than the
intrinsic severity of the risk. It is used in the **executive summary**
as a secondary sort: within each residual-risk tier, High-attention items
surface first. A Watchlist risk under active CFPB or FCA scrutiny warrants
different urgency than one flying under the radar.

---

## What the Outputs Show

### `output/risk_register.csv`
The complete 30-row register with every field and all four derived scores.
This is the master document the risk team maintains and updates regularly.

### `output/executive_summary.csv`
Filtered to **Escalate and Watchlist items only**. Sorted by residual risk
descending, then by regulatory attention (High → Medium → Low) within each
tier. Includes the `regulatory_attention` column so the committee can
immediately see which items are also under active regulator scrutiny.
This is what gets presented at a Risk Committee or board meeting —
leadership needs to see the items requiring attention, not the full register.

### `output/top_5_risks.csv`
The five risks with the highest residual score. A concise one-page summary
of the firm's most pressing emerging exposures.

### `output/risk_counts_by_category.csv`
Aggregated view showing, per category: total risks, count by status,
average residual score, and number of priority-flagged items. Shows
which *areas* of the firm carry the most concentrated emerging risk.

### `output/risk_heatmap.png`
A **Likelihood × Impact scatter chart** — the standard visual tool used
in risk management to present the portfolio at a glance.

- **x-axis:** Likelihood (1=Rare → 5=Almost Certain)
- **y-axis:** Impact (1=Negligible → 5=Critical)
- **Colour:** Green = Monitor · Orange = Watchlist · Red = Escalate
- **Star marker:** Priority-flagged items

The top-right quadrant is the danger zone. Items clustering there are the
ones a risk committee will ask about first.

---

## Relevance to Strategy and Emerging Risk Roles

This project mirrors the actual workflow of an emerging risk team:

| Step | Real-World Activity | In This Project |
|---|---|---|
| **Identify** | Horizon scanning, regulatory bulletins, internal nominations | 30 synthetic risks across 11 categories |
| **Score** | Risk committee scores likelihood, impact, velocity, controls | `scoring.py` — inherent risk = (L × I) + V; residual = inherent × (1 − CE) |
| **Triage** | Classify risks into governance action tiers | `risk_status` — Escalate / Watchlist / Monitor |
| **Prioritise** | Flag worsening high-exposure items for urgent action | `priority_flag` column |
| **Report** | Board packs, committee updates, category roll-ups | Executive summary, top-5, category counts |
| **Visualise** | Heat maps for Risk Committee and board presentations | `risk_heatmap.png` |

---

## Interview Talking Points

**On the inherent vs. residual distinction:**
> "Inherent risk tells you how bad a threat is if you do nothing. Residual
> risk tells you what's left after your controls are applied. That gap is
> where risk management actually lives — understanding how effective your
> controls are and where they fall short."

**On the heat map:**
> "The top-right quadrant is the danger zone — high likelihood and high
> impact. That's where your Escalate items cluster and the first place a
> Risk Committee looks. The chart makes the whole portfolio readable in
> under a minute."

**On velocity:**
> "Velocity is built into the inherent risk score — fast-moving threats get
> a higher score because they leave less time for controls to activate.
> A ransomware attack with velocity 5 scores (4×5)+5=25 inherent; the same
> likelihood and impact with velocity 2 scores only 22. It's a deliberate
> design choice: slow-burn risks like climate change or Basel IV aren't
> penalised because you multiply by velocity, but fast-movers get
> appropriate urgency credit."

**On the priority flag:**
> "The flag catches the intersection of two bad signals: residual exposure
> is already high, and the trend is worsening. That combination is what
> a Chief Risk Officer puts at the top of the board pack."
