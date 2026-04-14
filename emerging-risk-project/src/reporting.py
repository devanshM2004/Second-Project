"""
reporting.py
------------
Generates all output files from the scored risk register:

    output/risk_register.csv          -- full 30-row register
    output/executive_summary.csv      -- Escalate + Watchlist items only
    output/top_5_risks.csv            -- highest residual risk items
    output/risk_counts_by_category.csv -- aggregated view by category
    output/risk_heatmap.png           -- likelihood vs impact heat map
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


OUTPUT_DIR = "output"


def _ensure_output_dir():
    """Create the output directory if it does not already exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Report 1: Full Risk Register ───────────────────────────────────────────

def save_risk_register(df: pd.DataFrame) -> None:
    """Write the complete scored risk register to CSV."""
    path = os.path.join(OUTPUT_DIR, "risk_register.csv")
    df.to_csv(path, index=False)
    print(f"      Saved → {path}  ({len(df)} rows)")


# ── Report 2: Executive Summary ────────────────────────────────────────────

def save_executive_summary(df: pd.DataFrame) -> None:
    """
    Write a condensed view for senior leadership.

    Includes only Escalate and Watchlist items, with the columns
    a non-technical audience actually cares about.
    """
    cols = [
        "risk_id", "risk_name", "risk_category", "business_unit",
        "inherent_risk", "residual_risk", "risk_status",
        "trend_direction", "priority_flag", "owner",
        "mitigation_status", "next_review_date",
    ]

    summary = (
        df[df["risk_status"].isin(["Escalate", "Watchlist"])][cols]
        .sort_values("residual_risk", ascending=False)
        .reset_index(drop=True)
    )

    path = os.path.join(OUTPUT_DIR, "executive_summary.csv")
    summary.to_csv(path, index=False)
    print(f"      Saved → {path}  ({len(summary)} rows: "
          f"{(summary['risk_status']=='Escalate').sum()} Escalate, "
          f"{(summary['risk_status']=='Watchlist').sum()} Watchlist)")


# ── Report 3: Top 5 Risks ──────────────────────────────────────────────────

def save_top_5(df: pd.DataFrame) -> None:
    """Write the five highest residual-risk items to CSV."""
    cols = [
        "risk_id", "risk_name", "risk_category",
        "inherent_risk", "residual_risk", "risk_status",
        "trend_direction", "priority_flag", "owner",
    ]

    top5 = (
        df[cols]
        .sort_values("residual_risk", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )
    top5.index += 1  # rank starts at 1

    path = os.path.join(OUTPUT_DIR, "top_5_risks.csv")
    top5.to_csv(path)
    print(f"      Saved → {path}")
    print("\n      --- Top 5 Risks by Residual Score ---")
    print(top5[["risk_name", "residual_risk", "risk_status",
                "priority_flag"]].to_string())


# ── Report 4: Risk Counts by Category ─────────────────────────────────────

def save_category_counts(df: pd.DataFrame) -> None:
    """Aggregate risk counts and average residual score by category."""
    agg = (
        df.groupby("risk_category")
        .agg(
            total_risks=("risk_id", "count"),
            escalate=("risk_status", lambda x: (x == "Escalate").sum()),
            watchlist=("risk_status", lambda x: (x == "Watchlist").sum()),
            monitor=("risk_status", lambda x: (x == "Monitor").sum()),
            avg_residual_risk=("residual_risk", "mean"),
            priority_items=("priority_flag", "sum"),
        )
        .round({"avg_residual_risk": 2})
        .sort_values("avg_residual_risk", ascending=False)
        .reset_index()
    )

    path = os.path.join(OUTPUT_DIR, "risk_counts_by_category.csv")
    agg.to_csv(path, index=False)
    print(f"      Saved → {path}  ({len(agg)} categories)")


# ── Report 5: Heat Map ─────────────────────────────────────────────────────

def save_heatmap(df: pd.DataFrame) -> None:
    """
    Generate a Likelihood × Impact heat map coloured by risk status.

    - x-axis: Likelihood Score (1–5)
    - y-axis: Impact Score     (1–5)
    - colour: green=Monitor, orange=Watchlist, red=Escalate
    - marker: star (*) marks priority-flagged items

    The top-right quadrant (high likelihood, high impact) is where
    Escalate items cluster — exactly what you'd explain to a committee.
    """
    _ensure_output_dir()

    status_colors = {
        "Monitor":   "#2ca02c",   # green
        "Watchlist": "#ff7f0e",   # orange
        "Escalate":  "#d62728",   # red
    }

    fig, ax = plt.subplots(figsize=(10, 8))

    # Shade the four quadrants to give visual context
    ax.axhspan(3.5, 5.5, xmin=0.5, xmax=1.0, color="#ffe0e0", alpha=0.4, zorder=0)
    ax.axhspan(0.5, 3.5, xmin=0.0, xmax=0.5, color="#e8f5e9", alpha=0.4, zorder=0)

    # Plot each risk as a scatter point
    for _, row in df.iterrows():
        color = status_colors[row["risk_status"]]
        marker = "*" if row["priority_flag"] else "o"
        size   = 220 if row["priority_flag"] else 120

        ax.scatter(
            row["likelihood_score"],
            row["impact_score"],
            c=color,
            s=size,
            marker=marker,
            edgecolors="white",
            linewidths=0.6,
            zorder=3,
            alpha=0.88,
        )

        # Label each point with its risk_id — small, offset slightly
        ax.annotate(
            row["risk_id"],
            xy=(row["likelihood_score"], row["impact_score"]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=6.5,
            color="#333333",
        )

    # ── Axes and labels ────────────────────────────────────────────────
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(["1\nRare", "2\nUnlikely", "3\nPossible",
                         "4\nLikely", "5\nAlmost\nCertain"], fontsize=9)
    ax.set_yticklabels(["1\nNegligible", "2\nMinor", "3\nModerate",
                         "4\nMajor", "5\nCritical"], fontsize=9)
    ax.set_xlabel("Likelihood Score", fontsize=11, labelpad=10)
    ax.set_ylabel("Impact Score", fontsize=11, labelpad=10)
    ax.set_title(
        "Emerging Risk Heat Map — Likelihood vs. Impact",
        fontsize=13, fontweight="bold", pad=15,
    )

    # Quadrant labels
    ax.text(1.0, 5.1, "Low Likelihood\nHigh Impact",
            fontsize=7.5, color="#888888", ha="left")
    ax.text(4.2, 5.1, "High Likelihood\nHigh Impact  ►  Escalate",
            fontsize=7.5, color="#c0392b", ha="left")
    ax.text(1.0, 0.65, "Low Likelihood\nLow Impact  ►  Monitor",
            fontsize=7.5, color="#27ae60", ha="left")
    ax.text(4.2, 0.65, "High Likelihood\nLow Impact",
            fontsize=7.5, color="#888888", ha="left")

    # Grid
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)

    # ── Legend ─────────────────────────────────────────────────────────
    legend_handles = [
        mpatches.Patch(color=status_colors["Monitor"],   label="Monitor"),
        mpatches.Patch(color=status_colors["Watchlist"], label="Watchlist"),
        mpatches.Patch(color=status_colors["Escalate"],  label="Escalate"),
        plt.scatter([], [], marker="*", c="grey", s=120,
                    label="Priority Flag (Escalate + Increasing Trend)"),
    ]
    ax.legend(handles=legend_handles, loc="lower right",
              fontsize=9, framealpha=0.9)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "risk_heatmap.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"      Saved → {path}")


# ── Orchestrator ───────────────────────────────────────────────────────────

def generate_reports(df: pd.DataFrame) -> None:
    """Run all five report generators in sequence."""
    _ensure_output_dir()
    save_risk_register(df)
    save_executive_summary(df)
    save_top_5(df)
    save_category_counts(df)
    save_heatmap(df)
