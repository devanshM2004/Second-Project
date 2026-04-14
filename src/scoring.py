"""
scoring.py
----------
Applies inherent risk, residual risk, status labels, and priority flags
to the raw risk register DataFrame.

All logic is intentionally simple and transparent — easy to explain in
an interview or to a non-technical stakeholder.
"""

import pandas as pd


def apply_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add four derived columns to the risk register:

        inherent_risk  -- raw exposure before controls (uses likelihood,
                          impact, and velocity)
        residual_risk  -- exposure after controls are applied
        risk_status    -- Monitor / Watchlist / Escalate
        priority_flag  -- True if high residual AND trend is worsening

    Parameters
    ----------
    df : pd.DataFrame
        Output of data_generator.build_risk_register()

    Returns
    -------
    pd.DataFrame
        Same DataFrame with four new columns appended.
    """

    # ── 1. Inherent Risk ───────────────────────────────────────────────────
    # How severe is this risk BEFORE we do anything about it?
    #
    # Formula: (Likelihood × Impact) + Velocity
    #   - Likelihood × Impact captures severity: how probable × how damaging
    #     Scale: 1–25
    #   - Velocity is added on top as an urgency premium: fast-moving threats
    #     leave less time for controls to work, so they score higher
    #     Scale: adds 1–5 on top of the product
    #   - Combined inherent scale: 3–30
    #
    # Why not multiply by velocity?
    #   Multiplying would unfairly penalise slow-moving but severe risks
    #   (e.g. climate risk, Basel IV) — a deliberate design choice to
    #   keep slow-burn existential threats visible in the register.
    #
    # Interview example — Ransomware Attack:
    #   likelihood=4, impact=5, velocity=5
    #   → inherent = (4 × 5) + 5 = 25
    df["inherent_risk"] = (
        df["likelihood_score"] * df["impact_score"] + df["velocity_score"]
    )

    # ── 2. Residual Risk ───────────────────────────────────────────────────
    # How much risk REMAINS after existing controls do their job?
    #
    # Formula: Inherent Risk × (1 − Control Effectiveness)
    #   - control_effectiveness is stored as a decimal between 0 and 1
    #   - 0.00 = controls provide no protection whatsoever
    #   - 1.00 = controls fully eliminate the risk (rarely realistic)
    #   - 0.60 = controls reduce exposure by 60%, leaving 40% remaining
    #
    # Example — Ransomware Attack:
    #   inherent_risk=25, control_effectiveness=0.55
    #   → residual = 25 × (1 − 0.55) = 25 × 0.45 = 11.25  (Escalate)
    df["residual_risk"] = (
        df["inherent_risk"] * (1 - df["control_effectiveness"])
    ).round(2)

    # ── 3. Risk Status ─────────────────────────────────────────────────────
    # Translate the residual score into an actionable triage label.
    #
    # Thresholds are calibrated to the residual risk range in this portfolio.
    # With inherent scores ranging 5–25 and control effectiveness 25–70%,
    # residual scores cluster between 3 and 14:
    #
    #   Escalate  (≥ 11): Immediate senior leadership attention required.
    #   Watchlist (≥  7): Elevated — review monthly, escalation criteria set.
    #   Monitor   (<  7): Acceptable — standard quarterly review cycle.
    def assign_status(residual: float) -> str:
        if residual >= 11:
            return "Escalate"
        elif residual >= 7:
            return "Watchlist"
        else:
            return "Monitor"

    df["risk_status"] = df["residual_risk"].apply(assign_status)

    # ── 4. Priority Flag ───────────────────────────────────────────────────
    # Mark risks that are BOTH at the Escalate tier AND actively worsening.
    # These are the items most likely to surprise leadership if left alone.
    #
    # Criteria:
    #   - residual_risk ≥ 11   (Escalate tier)
    #   - trend_direction == "Increasing"  (trajectory is worsening)
    #
    # A priority-flagged risk has two bad signals at once: the residual
    # exposure is already high despite controls, and the trend is moving
    # in the wrong direction. This is what a CRO puts at the top of a board
    # pack.
    df["priority_flag"] = (
        (df["residual_risk"] >= 11) & (df["trend_direction"] == "Increasing")
    )

    return df
