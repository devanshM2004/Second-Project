"""
data_generator.py
-----------------
Creates a synthetic dataset of 30 realistic emerging risks for a large
financial institution.  Every value is hard-coded (no random seed tricks)
so the numbers are stable, explainable, and easy to walk through in an
interview.
"""

import pandas as pd
from datetime import date


def build_risk_register() -> pd.DataFrame:
    """Return a DataFrame with 30 emerging-risk records."""

    risks = [
        # ── Cybersecurity ──────────────────────────────────────────────────
        {
            "risk_id": "ER-001",
            "risk_name": "Ransomware Attack on Core Banking Systems",
            "risk_category": "Cybersecurity",
            "business_unit": "IT / Technology",
            "description": (
                "Threat actors deploy ransomware targeting core banking "
                "infrastructure, causing prolonged outages and potential "
                "data exfiltration."
            ),
            "likelihood_score": 4,
            "impact_score": 5,
            "velocity_score": 5,
            "control_effectiveness": 0.55,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Chief Information Security Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 12, 15),
            "next_review_date": date(2026, 3, 15),
        },
        {
            "risk_id": "ER-002",
            "risk_name": "Third-Party API Breach via Vendor Integration",
            "risk_category": "Cybersecurity",
            "business_unit": "Operations",
            "description": (
                "A compromised third-party fintech API exposes customer "
                "account data and enables unauthorized fund transfers."
            ),
            "likelihood_score": 3,
            "impact_score": 4,
            "velocity_score": 4,
            "control_effectiveness": 0.50,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Head of Third-Party Risk",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 11, 1),
            "next_review_date": date(2026, 2, 1),
        },
        {
            "risk_id": "ER-003",
            "risk_name": "AI-Powered Phishing and Social Engineering",
            "risk_category": "Cybersecurity",
            "business_unit": "Retail Banking",
            "description": (
                "Generative AI enables hyper-personalised phishing campaigns "
                "targeting employees and customers, increasing credential theft."
            ),
            "likelihood_score": 4,
            "impact_score": 3,
            "velocity_score": 4,
            "control_effectiveness": 0.45,
            "regulatory_attention": "Medium",
            "trend_direction": "Increasing",
            "owner": "Chief Information Security Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 10),
            "next_review_date": date(2026, 4, 10),
        },
        # ── Regulatory / Compliance ────────────────────────────────────────
        {
            "risk_id": "ER-004",
            "risk_name": "Basel IV Capital Requirements Implementation",
            "risk_category": "Regulatory / Compliance",
            "business_unit": "Risk Management",
            "description": (
                "Revised Basel IV output floors require higher risk-weighted "
                "assets, potentially constraining lending capacity and ROE."
            ),
            "likelihood_score": 5,
            "impact_score": 4,
            "velocity_score": 2,
            "control_effectiveness": 0.65,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Chief Risk Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 10, 20),
            "next_review_date": date(2026, 4, 20),
        },
        {
            "risk_id": "ER-005",
            "risk_name": "Digital Asset Regulatory Uncertainty",
            "risk_category": "Regulatory / Compliance",
            "business_unit": "Compliance",
            "description": (
                "Rapidly evolving global crypto/digital-asset regulations create "
                "compliance gaps and potential enforcement actions."
            ),
            "likelihood_score": 4,
            "impact_score": 3,
            "velocity_score": 3,
            "control_effectiveness": 0.40,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Chief Compliance Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 5),
            "next_review_date": date(2026, 4, 5),
        },
        {
            "risk_id": "ER-006",
            "risk_name": "Consumer Protection Rule Changes (CFPB)",
            "risk_category": "Regulatory / Compliance",
            "business_unit": "Retail Banking",
            "description": (
                "New CFPB rulemaking on overdraft fees and credit card late "
                "charges reduces fee income and requires product redesign."
            ),
            "likelihood_score": 4,
            "impact_score": 3,
            "velocity_score": 2,
            "control_effectiveness": 0.60,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Chief Compliance Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 11, 15),
            "next_review_date": date(2026, 2, 15),
        },
        # ── Climate / ESG ──────────────────────────────────────────────────
        {
            "risk_id": "ER-007",
            "risk_name": "Physical Climate Risk in Mortgage Portfolio",
            "risk_category": "Climate / ESG",
            "business_unit": "Retail Banking",
            "description": (
                "Increased frequency of floods and wildfires impairs collateral "
                "values and drives mortgage defaults in exposed geographies."
            ),
            "likelihood_score": 3,
            "impact_score": 5,
            "velocity_score": 2,
            "control_effectiveness": 0.35,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Head of Credit Risk",
            "mitigation_status": "Not Started",
            "last_review_date": date(2025, 9, 30),
            "next_review_date": date(2026, 3, 30),
        },
        {
            "risk_id": "ER-008",
            "risk_name": "Transition Risk from Carbon Pricing Legislation",
            "risk_category": "Climate / ESG",
            "business_unit": "Investment Banking",
            "description": (
                "Carbon tax legislation impairs the credit quality of carbon-"
                "intensive borrowers and strands assets in the loan book."
            ),
            "likelihood_score": 3,
            "impact_score": 4,
            "velocity_score": 2,
            "control_effectiveness": 0.40,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Chief Sustainability Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 12, 1),
            "next_review_date": date(2026, 6, 1),
        },
        {
            "risk_id": "ER-009",
            "risk_name": "Greenwashing Enforcement and Reputational Risk",
            "risk_category": "Climate / ESG",
            "business_unit": "Asset Management",
            "description": (
                "Regulators increase scrutiny of ESG fund labelling; misleading "
                "disclosures expose the firm to fines and reputational damage."
            ),
            "likelihood_score": 3,
            "impact_score": 3,
            "velocity_score": 3,
            "control_effectiveness": 0.55,
            "regulatory_attention": "Medium",
            "trend_direction": "Increasing",
            "owner": "Chief Compliance Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 20),
            "next_review_date": date(2026, 4, 20),
        },
        # ── Geopolitical ───────────────────────────────────────────────────
        {
            "risk_id": "ER-010",
            "risk_name": "US–China Trade War Escalation",
            "risk_category": "Geopolitical",
            "business_unit": "Investment Banking",
            "description": (
                "Escalating tariffs and export controls disrupt global supply "
                "chains, compress corporate margins, and increase credit losses."
            ),
            "likelihood_score": 4,
            "impact_score": 4,
            "velocity_score": 3,
            "control_effectiveness": 0.30,
            "regulatory_attention": "Medium",
            "trend_direction": "Increasing",
            "owner": "Head of Country Risk",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 2, 1),
            "next_review_date": date(2026, 5, 1),
        },
        {
            "risk_id": "ER-011",
            "risk_name": "Sanctions Evasion and Correspondent Banking Risk",
            "risk_category": "Geopolitical",
            "business_unit": "Compliance",
            "description": (
                "State-sponsored actors exploit shell companies to evade "
                "sanctions; exposure risks severe regulatory penalties."
            ),
            "likelihood_score": 3,
            "impact_score": 5,
            "velocity_score": 4,
            "control_effectiveness": 0.60,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Chief Compliance Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 10, 10),
            "next_review_date": date(2026, 1, 10),
        },
        {
            "risk_id": "ER-012",
            "risk_name": "Middle East Conflict Spillover on Energy Markets",
            "risk_category": "Geopolitical",
            "business_unit": "Treasury",
            "description": (
                "Regional conflict causes oil price spikes that accelerate "
                "inflation, pressure central bank policy, and squeeze margins."
            ),
            "likelihood_score": 3,
            "impact_score": 3,
            "velocity_score": 4,
            "control_effectiveness": 0.25,
            "regulatory_attention": "Low",
            "trend_direction": "Stable",
            "owner": "Head of Market Risk",
            "mitigation_status": "Not Started",
            "last_review_date": date(2025, 12, 10),
            "next_review_date": date(2026, 3, 10),
        },
        # ── Technology / AI ────────────────────────────────────────────────
        {
            "risk_id": "ER-013",
            "risk_name": "Algorithmic Model Bias in Credit Decisioning",
            "risk_category": "Technology / AI",
            "business_unit": "Retail Banking",
            "description": (
                "ML credit models exhibit disparate impact on protected classes, "
                "triggering fair-lending enforcement and class-action litigation."
            ),
            "likelihood_score": 3,
            "impact_score": 4,
            "velocity_score": 3,
            "control_effectiveness": 0.50,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Chief Data Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 15),
            "next_review_date": date(2026, 4, 15),
        },
        {
            "risk_id": "ER-014",
            "risk_name": "Core System Modernisation Programme Overrun",
            "risk_category": "Technology / AI",
            "business_unit": "IT / Technology",
            "description": (
                "Legacy core-banking migration faces cost overruns and delays, "
                "increasing operational risk and diverting strategic investment."
            ),
            "likelihood_score": 4,
            "impact_score": 4,
            "velocity_score": 2,
            "control_effectiveness": 0.45,
            "regulatory_attention": "Medium",
            "trend_direction": "Stable",
            "owner": "Chief Technology Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 11, 20),
            "next_review_date": date(2026, 2, 20),
        },
        {
            "risk_id": "ER-015",
            "risk_name": "Quantum Computing Threat to Encryption",
            "risk_category": "Technology / AI",
            "business_unit": "IT / Technology",
            "description": (
                "Advances in quantum computing threaten RSA/ECC encryption used "
                "to protect transactions and customer data."
            ),
            "likelihood_score": 2,
            "impact_score": 5,
            "velocity_score": 2,
            "control_effectiveness": 0.70,
            "regulatory_attention": "Medium",
            "trend_direction": "Increasing",
            "owner": "Chief Information Security Officer",
            "mitigation_status": "Not Started",
            "last_review_date": date(2025, 9, 1),
            "next_review_date": date(2026, 9, 1),
        },
        # ── Market Risk ────────────────────────────────────────────────────
        {
            "risk_id": "ER-016",
            "risk_name": "Commercial Real Estate Valuation Collapse",
            "risk_category": "Market Risk",
            "business_unit": "Investment Banking",
            "description": (
                "Persistent remote-work trends depress office valuations, "
                "generating mark-to-market losses and covenant breaches in CRE "
                "loan portfolio."
            ),
            "likelihood_score": 4,
            "impact_score": 4,
            "velocity_score": 2,
            "control_effectiveness": 0.45,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Head of Credit Risk",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 2, 5),
            "next_review_date": date(2026, 5, 5),
        },
        {
            "risk_id": "ER-017",
            "risk_name": "Interest Rate Volatility and NIM Compression",
            "risk_category": "Market Risk",
            "business_unit": "Treasury",
            "description": (
                "Unexpected rate cuts compress net interest margins faster than "
                "liability repricing, pressuring earnings guidance."
            ),
            "likelihood_score": 3,
            "impact_score": 4,
            "velocity_score": 3,
            "control_effectiveness": 0.60,
            "regulatory_attention": "Medium",
            "trend_direction": "Stable",
            "owner": "Head of Market Risk",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 25),
            "next_review_date": date(2026, 4, 25),
        },
        {
            "risk_id": "ER-018",
            "risk_name": "Liquidity Crunch from Deposit Outflows",
            "risk_category": "Market Risk",
            "business_unit": "Treasury",
            "description": (
                "Social-media-amplified bank-run dynamics cause rapid deposit "
                "outflows, straining liquidity coverage ratios."
            ),
            "likelihood_score": 2,
            "impact_score": 5,
            "velocity_score": 5,
            "control_effectiveness": 0.65,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Chief Financial Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 12, 20),
            "next_review_date": date(2026, 3, 20),
        },
        # ── Operational Risk ───────────────────────────────────────────────
        {
            "risk_id": "ER-019",
            "risk_name": "Critical Cloud Provider Outage",
            "risk_category": "Operational Risk",
            "business_unit": "IT / Technology",
            "description": (
                "Over-reliance on a single hyperscaler cloud provider means a "
                "major outage halts payments, trading, and customer access."
            ),
            "likelihood_score": 3,
            "impact_score": 5,
            "velocity_score": 5,
            "control_effectiveness": 0.50,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Chief Technology Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 8),
            "next_review_date": date(2026, 4, 8),
        },
        {
            "risk_id": "ER-020",
            "risk_name": "Talent Attrition in Risk and Compliance Functions",
            "risk_category": "Operational Risk",
            "business_unit": "Human Resources",
            "description": (
                "High turnover among risk, compliance, and audit professionals "
                "creates knowledge gaps and weakens the control environment."
            ),
            "likelihood_score": 4,
            "impact_score": 3,
            "velocity_score": 2,
            "control_effectiveness": 0.40,
            "regulatory_attention": "Low",
            "trend_direction": "Increasing",
            "owner": "Chief Human Resources Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 11, 5),
            "next_review_date": date(2026, 2, 5),
        },
        {
            "risk_id": "ER-021",
            "risk_name": "Payment Processing Fraud via Synthetic Identities",
            "risk_category": "Operational Risk",
            "business_unit": "Retail Banking",
            "description": (
                "Fraudsters use AI to create synthetic identities that pass KYC "
                "checks, enabling large-scale first-party fraud losses."
            ),
            "likelihood_score": 4,
            "impact_score": 3,
            "velocity_score": 4,
            "control_effectiveness": 0.50,
            "regulatory_attention": "Medium",
            "trend_direction": "Increasing",
            "owner": "Head of Fraud Risk",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 2, 10),
            "next_review_date": date(2026, 5, 10),
        },
        # ── Credit Risk ────────────────────────────────────────────────────
        {
            "risk_id": "ER-022",
            "risk_name": "Consumer Credit Deterioration from Stagflation",
            "risk_category": "Credit Risk",
            "business_unit": "Retail Banking",
            "description": (
                "Prolonged stagflation erodes real household incomes, driving "
                "elevated credit-card and personal-loan delinquency rates."
            ),
            "likelihood_score": 3,
            "impact_score": 4,
            "velocity_score": 2,
            "control_effectiveness": 0.55,
            "regulatory_attention": "Medium",
            "trend_direction": "Increasing",
            "owner": "Head of Credit Risk",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 30),
            "next_review_date": date(2026, 4, 30),
        },
        {
            "risk_id": "ER-023",
            "risk_name": "Leveraged Loan Portfolio Stress",
            "risk_category": "Credit Risk",
            "business_unit": "Investment Banking",
            "description": (
                "Rising defaults among highly leveraged borrowers generate "
                "mark-to-market losses and increased provision charges."
            ),
            "likelihood_score": 3,
            "impact_score": 4,
            "velocity_score": 3,
            "control_effectiveness": 0.50,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Head of Credit Risk",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 12, 5),
            "next_review_date": date(2026, 3, 5),
        },
        {
            "risk_id": "ER-024",
            "risk_name": "Sovereign Debt Contagion in Emerging Markets",
            "risk_category": "Credit Risk",
            "business_unit": "Investment Banking",
            "description": (
                "Debt restructurings in key EM economies trigger contagion, "
                "causing credit spread widening and write-downs in EM exposure."
            ),
            "likelihood_score": 2,
            "impact_score": 4,
            "velocity_score": 4,
            "control_effectiveness": 0.45,
            "regulatory_attention": "Medium",
            "trend_direction": "Stable",
            "owner": "Head of Country Risk",
            "mitigation_status": "Not Started",
            "last_review_date": date(2025, 10, 25),
            "next_review_date": date(2026, 4, 25),
        },
        # ── Third-Party / Vendor ───────────────────────────────────────────
        {
            "risk_id": "ER-025",
            "risk_name": "Critical Vendor Insolvency (Payment Rail Provider)",
            "risk_category": "Third-Party / Vendor",
            "business_unit": "Operations",
            "description": (
                "Insolvency of a key payment-rail technology vendor disrupts "
                "domestic transaction processing for retail and corporate clients."
            ),
            "likelihood_score": 2,
            "impact_score": 5,
            "velocity_score": 4,
            "control_effectiveness": 0.40,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Head of Third-Party Risk",
            "mitigation_status": "Not Started",
            "last_review_date": date(2025, 9, 15),
            "next_review_date": date(2026, 3, 15),
        },
        {
            "risk_id": "ER-026",
            "risk_name": "Data Localisation Laws Impacting Cloud Strategy",
            "risk_category": "Third-Party / Vendor",
            "business_unit": "IT / Technology",
            "description": (
                "New data-residency requirements in multiple jurisdictions force "
                "costly infrastructure changes and limit cloud provider choice."
            ),
            "likelihood_score": 4,
            "impact_score": 3,
            "velocity_score": 2,
            "control_effectiveness": 0.50,
            "regulatory_attention": "Medium",
            "trend_direction": "Increasing",
            "owner": "Chief Technology Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 12),
            "next_review_date": date(2026, 4, 12),
        },
        # ── Strategic Risk ─────────────────────────────────────────────────
        {
            "risk_id": "ER-027",
            "risk_name": "Fintech Disintermediation of Retail Deposits",
            "risk_category": "Strategic Risk",
            "business_unit": "Corporate Strategy",
            "description": (
                "High-yield fintech savings products accelerate deposit migration "
                "from incumbent banks, raising funding costs and reducing the "
                "core deposit franchise."
            ),
            "likelihood_score": 4,
            "impact_score": 3,
            "velocity_score": 3,
            "control_effectiveness": 0.35,
            "regulatory_attention": "Low",
            "trend_direction": "Increasing",
            "owner": "Chief Strategy Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 2, 15),
            "next_review_date": date(2026, 5, 15),
        },
        {
            "risk_id": "ER-028",
            "risk_name": "Generative AI Adoption without Governance Framework",
            "risk_category": "Strategic Risk",
            "business_unit": "Corporate Strategy",
            "description": (
                "Rapid internal deployment of GenAI tools outpaces governance, "
                "creating model-risk, IP, and data-privacy exposures."
            ),
            "likelihood_score": 4,
            "impact_score": 4,
            "velocity_score": 4,
            "control_effectiveness": 0.30,
            "regulatory_attention": "High",
            "trend_direction": "Increasing",
            "owner": "Chief Risk Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 2, 20),
            "next_review_date": date(2026, 5, 20),
        },
        # ── Conduct / Legal ────────────────────────────────────────────────
        {
            "risk_id": "ER-029",
            "risk_name": "Mis-selling Risk in Structured Products",
            "risk_category": "Conduct / Legal",
            "business_unit": "Investment Banking",
            "description": (
                "Complex structured notes are sold to retail investors without "
                "adequate suitability assessment, risking FCA enforcement and "
                "class-action redress."
            ),
            "likelihood_score": 3,
            "impact_score": 4,
            "velocity_score": 2,
            "control_effectiveness": 0.55,
            "regulatory_attention": "High",
            "trend_direction": "Stable",
            "owner": "Chief Compliance Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2025, 11, 25),
            "next_review_date": date(2026, 2, 25),
        },
        {
            "risk_id": "ER-030",
            "risk_name": "Insider Threat and Data Theft by Departing Staff",
            "risk_category": "Conduct / Legal",
            "business_unit": "Human Resources",
            "description": (
                "Departing employees exfiltrate sensitive client data or "
                "intellectual property, leading to regulatory investigations and "
                "litigation."
            ),
            "likelihood_score": 3,
            "impact_score": 3,
            "velocity_score": 3,
            "control_effectiveness": 0.60,
            "regulatory_attention": "Medium",
            "trend_direction": "Stable",
            "owner": "Chief Information Security Officer",
            "mitigation_status": "In Progress",
            "last_review_date": date(2026, 1, 22),
            "next_review_date": date(2026, 4, 22),
        },
    ]

    df = pd.DataFrame(risks)

    # Ensure date columns are proper Python date objects
    df["last_review_date"] = pd.to_datetime(df["last_review_date"])
    df["next_review_date"] = pd.to_datetime(df["next_review_date"])

    return df


if __name__ == "__main__":
    df = build_risk_register()
    print(f"Dataset shape: {df.shape}")
    print(df[["risk_id", "risk_name", "risk_category"]].to_string(index=False))
