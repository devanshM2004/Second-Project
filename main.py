"""
main.py
-------
Entry point for the Emerging Risk Identification and Monitoring Framework.

Pipeline:
    1. Build the synthetic risk register (30 risks, 15 fields each)
    2. Apply scoring logic (inherent risk, residual risk, status, priority flag)
    3. Generate output reports and heat map chart

Run:
    python main.py
"""

from src.data_generator import build_risk_register
from src.scoring import apply_scores
from src.reporting import generate_reports


def main():
    print("=" * 60)
    print("  Emerging Risk Identification and Monitoring Framework")
    print("=" * 60)

    # ── Step 1: Build synthetic risk register ──────────────────
    print("\n[1/3] Building synthetic risk register...")
    df = build_risk_register()
    print(f"      {len(df)} risks loaded across "
          f"{df['risk_category'].nunique()} categories.")

    # Save the unscored input dataset to data/ for reference
    df.to_csv("data/risk_register_raw.csv", index=False)

    # ── Step 2: Apply scoring logic ────────────────────────────
    print("\n[2/3] Applying scoring logic...")
    df = apply_scores(df)

    status_counts = df["risk_status"].value_counts()
    priority_count = df["priority_flag"].sum()
    print(f"      Escalate:  {status_counts.get('Escalate',  0):>2} risks")
    print(f"      Watchlist: {status_counts.get('Watchlist', 0):>2} risks")
    print(f"      Monitor:   {status_counts.get('Monitor',   0):>2} risks")
    print(f"      Priority flagged: {priority_count} "
          "(Escalate tier + Increasing trend)")

    # ── Step 3: Generate reports and heat map ──────────────────
    print("\n[3/3] Generating reports and heat map...")
    generate_reports(df)

    print("\n" + "=" * 60)
    print("  Complete. Outputs written to output/")
    print("=" * 60)


if __name__ == "__main__":
    main()
