# Emerging Risk Identification and Monitoring Framework

## Business Purpose

Large financial institutions face a constantly shifting landscape of threats — from
cyberattacks and regulatory changes to climate events and geopolitical instability.
A dedicated **Strategy & Emerging Risk** team is responsible for:

1. **Identifying** risks before they become crises
2. **Scoring** them on likelihood, impact, and speed of onset (velocity)
3. **Prioritizing** which risks demand immediate attention vs. ongoing monitoring
4. **Reporting** findings to senior leadership and the board

This project simulates that workflow end-to-end using Python and pandas, producing
the same types of outputs (risk registers, executive summaries, heat maps) that a
real risk analyst would deliver to stakeholders.

---

## Project Structure

```
emerging-risk-project/
├── data/               # Raw / synthetic input data
├── output/             # Generated reports and charts
├── src/
│   ├── data_generator.py   # Creates the synthetic risk dataset
│   ├── scoring.py          # Inherent / residual risk scoring logic
│   └── reporting.py        # CSV exports and heat map chart
├── main.py             # Entry point — runs the full pipeline
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
```

Outputs are written to the `output/` folder:
| File | Description |
|------|-------------|
| `risk_register.csv` | Full 30-row risk register with all scores |
| `executive_summary.csv` | High-priority risks for leadership review |
| `top_5_risks.csv` | The five highest residual-risk items |
| `risk_counts_by_category.csv` | Aggregated risk counts per category |
| `risk_heatmap.png` | Likelihood vs. Impact heat map chart |

---

## Scoring Methodology

| Metric | Formula |
|--------|---------|
| **Inherent Risk** | `likelihood × impact` (raw exposure, 1–25) |
| **Residual Risk** | `inherent_risk × (1 − control_effectiveness)` |
| **Risk Status** | Escalate ≥ 15 · Watchlist ≥ 9 · Monitor < 9 (residual) |
| **Priority Flag** | Residual ≥ 12 **and** trend = Increasing |

---

## Interview Talking Points

- "I built a synthetic risk register that mirrors what a real emerging-risk team
  would maintain, then applied a scoring model used in practice."
- "The heat map gives a quick visual to leadership: top-right quadrant means
  high likelihood AND high impact — those are your Escalate items."
- "Control effectiveness acts as a discount factor — a risk with great controls
  has a much lower residual score even if its inherent exposure is high."
- "Velocity captures how fast a risk can escalate; a slow-moving regulatory change
  behaves very differently from a sudden cyber incident."
