from investment_analyzer.core.portfolio_storage import load_portfolio
from investment_analyzer.reports.report_manager import ReportManager


print()
print("MONTE CARLO WITHDRAWAL REPORT TEST")
print("=" * 60)

portfolio = load_portfolio("Version_4_Test.json")

manager = ReportManager()

filename = manager.create_withdrawal_report(
    portfolio=portfolio,
    initial_value=500000.0,
    annual_withdrawal=25000.0,
    years=10,
    simulations=10000,
    seed=42,
)

print()
print("Withdrawal sustainability report created:")
print(filename)

assert filename.exists()
print("Report file verification passed.")

text = filename.read_text()

required_text = [
    "Withdrawal Sustainability Analysis Report",
    "Version 4 Test",
    "$500,000.00",
    "$25,000.00",
    "5.00%",
    "10 years",
    "10,000",
    "Survival Probability",
    "Depletion Probability",
    "10th Percentile",
    "25th Percentile",
    "Median",
    "75th Percentile",
    "90th Percentile",
    "Mean Ending Value",
    "not forecasts or guarantees",
]

for item in required_text:
    assert item in text, (
        f"Expected report text not found: {item}"
    )

print("Report content verification passed.")

print()
print("All Monte Carlo withdrawal report tests passed.")
