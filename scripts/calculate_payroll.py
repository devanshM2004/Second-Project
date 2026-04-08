import pandas as pd

df = pd.read_csv("data/sample_payroll_data.csv")

df["regular_pay"] = df["hourly_rate"] * df["regular_hours"]
df["overtime_pay"] = df["hourly_rate"] * 1.5 * df["overtime_hours"]
df["gross_pay"] = df["regular_pay"] + df["overtime_pay"]

df["tax"] = df["gross_pay"] * 0.18
df["total_deductions"] = df["tax"] + df["benefit_deduction"] + df["other_deduction"]

df["net_pay"] = df["gross_pay"] - df["total_deductions"]

df["variance"] = df["net_pay"] - df["prior_period_net_pay"]
df["variance_percent"] = (df["variance"] / df["prior_period_net_pay"]) * 100.00

df["flag"] = df["variance_percent"].abs() > 10.00

df.to_csv("outputs/payroll_output.csv", index=False)

print("Done.")