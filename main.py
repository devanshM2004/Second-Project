"""
main.py
-------
Entry point for the Emerging Risk Identification and Monitoring Framework.

Pipeline:
    1. Build synthetic risk register (30 risks, 15 fields)
    2. Apply scoring (inherent risk, residual risk, status, priority flag)
    3. Generate output reports (4 CSVs)
    4. Generate risk heat map chart (PNG)

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
    print("\n[1/4] Building synthetic risk register...")
    df = build_risk_register()
    print(f"      Loaded {len(df)} emerging risks across "
          f"{df['risk_category'].nunique()} categories.")

    # ── Step 2: Apply scoring logic ────────────────────────────
    print("\n[2/4] Applying scoring logic...")
    df = apply_scores(df)

    status_counts = df["risk_status"].value_counts()
    priority_count = df["priority_flag"].sum()
    print(f"      Escalate:  {status_counts.get('Escalate',  0):>2} risks")
    print(f"      Watchlist: {status_counts.get('Watchlist', 0):>2} risks")
    print(f"      Monitor:   {status_counts.get('Monitor',   0):>2} risks")
    print(f"      Priority flagged: {priority_count} risks "
          "(high residual + increasing trend)")

    # Save scored register to data/ for reference
    df.to_csv("data/risk_register_raw.csv", index=False)

    # ── Step 3 & 4: Generate reports and heat map ──────────────
    print("\n[3/4] Generating output reports...")
    print("[4/4] Generating risk heat map...")
    generate_reports(df)

    print("\n" + "=" * 60)
    print("  Pipeline complete. Outputs written to output/")
    print("=" * 60)


if __name__ == "__main__":
    main()
