"""
main.py
-------
Entry point for the Emerging Risk Identification and Monitoring Framework.
Run:  python main.py
"""

from src.data_generator import build_risk_register


def main():
    print("=" * 60)
    print("  Emerging Risk Identification and Monitoring Framework")
    print("=" * 60)

    # ── Step 1: Build synthetic risk register ──────────────────
    print("\n[1/4] Building synthetic risk register...")
    df = build_risk_register()
    print(f"      Loaded {len(df)} emerging risks across "
          f"{df['risk_category'].nunique()} categories.\n")

    # Save raw dataset to data/
    df.to_csv("data/risk_register_raw.csv", index=False)
    print("      Saved → data/risk_register_raw.csv")

    # Quick preview
    print("\n--- Risk Register Preview (first 5 rows) ---")
    preview_cols = ["risk_id", "risk_name", "risk_category",
                    "likelihood_score", "impact_score", "control_effectiveness"]
    print(df[preview_cols].head().to_string(index=False))

    # ── Steps 2-4 coming in next phase ─────────────────────────
    print("\n[2/4] Scoring logic      — coming next")
    print("[3/4] Report generation  — coming next")
    print("[4/4] Heat map chart     — coming next")
    print("\nDone.")


if __name__ == "__main__":
    main()
