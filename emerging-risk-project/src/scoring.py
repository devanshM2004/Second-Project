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

        inherent_risk      -- raw exposure before controls
        residual_risk      -- exposure after controls are applied
        risk_status        -- Monitor / Watchlist / Escalate
        priority_flag      -- True if high residual AND trend is worsening

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
    # Scale: 1 (low) to 25 (critical)
    #
    # Formula: Likelihood × Impact
    #   - Likelihood: how probable is the risk event?   (1–5)
    #   - Impact:     how bad would the damage be?      (1–5)
    #
    # A score of 25 means both are at maximum — the worst possible exposure.
    df["inherent_risk"] = df["likelihood_score"] * df["impact_score"]

    # ── 2. Residual Risk ───────────────────────────────────────────────────
    # How much risk REMAINS after existing controls do their job?
    #
    # Formula: Inherent Risk × (1 − Control Effectiveness)
    #   - control_effectiveness is stored as a decimal between 0 and 1
    #   - 0.00 = controls provide no protection whatsoever
    #   - 1.00 = controls fully eliminate the risk (rarely realistic)
    #   - 0.60 = controls reduce exposure by 60%, leaving 40% remaining
    #
    # Example: inherent_risk=20, control_effectiveness=0.60
    #   → residual_risk = 20 × (1 − 0.60) = 20 × 0.40 = 8.0  (Watchlist)
    df["residual_risk"] = (
        df["inherent_risk"] * (1 - df["control_effectiveness"])
    ).round(2)

    # ── 3. Risk Status ─────────────────────────────────────────────────────
    # Translate the residual score into an actionable triage label.
    #
    # Why these thresholds?
    # Inherent risk tops out at 25 (5×5). Control effectiveness in this
    # portfolio averages 45–65%, so residual scores cluster in the 3–12
    # range rather than 1–25. Thresholds are calibrated to that range:
    #
    #   Escalate  (≥  9): Senior leadership must act now.
    #   Watchlist (≥  6): Elevated — review monthly, ready to escalate.
    #   Monitor   (<  6): Acceptable level — standard quarterly cycle.
    def assign_status(residual: float) -> str:
        if residual >= 9:
            return "Escalate"
        elif residual >= 6:
            return "Watchlist"
        else:
            return "Monitor"

    df["risk_status"] = df["residual_risk"].apply(assign_status)

    # ── 4. Priority Flag ───────────────────────────────────────────────────
    # Highlight risks that are BOTH high in residual score AND getting worse.
    # These are the items most likely to surprise leadership if left alone.
    #
    # Criteria:
    #   - residual_risk ≥ 9    (Escalate tier)
    #   - trend_direction == "Increasing"  (trajectory is worsening)
    df["priority_flag"] = (
        (df["residual_risk"] >= 9) & (df["trend_direction"] == "Increasing")
    )

    return df
