import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
data_file = base_dir / 'data' / 'sample_payroll_data.csv'
outputs_dir = base_dir / 'outputs'
outputs_dir.mkdir(exist_ok=True)

payroll = pd.read_csv(data_file)

payroll['regular_pay'] = payroll['hourly_rate'] * payroll['regular_hours']
payroll['overtime_pay'] = payroll['hourly_rate'] * 1.5 * payroll['overtime_hours']
payroll['gross_pay'] = payroll['regular_pay'] + payroll['overtime_pay']
payroll['tax_withholding'] = payroll['gross_pay'] * 0.18
payroll['total_deductions'] = payroll['tax_withholding'] + payroll['benefit_deduction'] + payroll['other_deduction']
payroll['net_pay'] = payroll['gross_pay'] - payroll['total_deductions']
payroll['net_pay_variance'] = payroll['net_pay'] - payroll['prior_period_net_pay']
payroll['variance_percent'] = (payroll['net_pay_variance'] / payroll['prior_period_net_pay']) * 100
payroll['review_flag'] = payroll['variance_percent'].abs() > 10.0

summary_file = outputs_dir / 'payroll_summary.csv'
variance_file = outputs_dir / 'payroll_variance_report.csv'

payroll.to_csv(summary_file, index=False)
payroll[payroll['review_flag']].to_csv(variance_file, index=False)

print('Payroll files created successfully.')
