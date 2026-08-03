from investment_analyzer.core.portfolio_storage import load_portfolio
from investment_analyzer.reports.report_manager import ReportManager


print()
print("WITHDRAWAL STRATEGY COMPARISON REPORT TEST")
print("=" * 60)

portfolio = load_portfolio("Version_4_Test.json")

manager = ReportManager()

withdrawal_amounts = [
    20000.0,
    25000.0,
    30000.0,
    35000.0,
]

filename = manager.create_withdrawal_strategy_comparison_report(
    portfolio=portfolio,
    initial_value=500000.0,
    annual_withdrawals=withdrawal_amounts,
    years=20,
    simulations=10000,
    seed=42,
    inflation_rate=0.03,
)

print()
print("Withdrawal strategy comparison report created:")
print(filename)

assert filename.exists()
print("Report file verification passed.")

text = filename.read_text()

required_text = [
    "Withdrawal Strategy Comparison Report",
    "Version 4 Test",
    "$500,000.00",
    "20 years",
    "3.00%",
    "10,000",
    "VBIAX",
    "VWENX",
    "Withdrawal Strategy Comparison",
    "Withdrawal",
    "Rate",
    "Survival",
    "Depletion",
    "Median Ending",
    "$    20,000.00",
    "$    25,000.00",
    "$    30,000.00",
    "$    35,000.00",
    "4.00%",
    "5.00%",
    "6.00%",
    "7.00%",
    "Higher withdrawals generally increase depletion risk",
    "not forecasts or guarantees",
]

for item in required_text:
    assert item in text, (
        f"Expected report text not found: {item}"
    )

print("Report content verification passed.")

assert text.index("$    20,000.00") < text.index("$    25,000.00")
assert text.index("$    25,000.00") < text.index("$    30,000.00")
assert text.index("$    30,000.00") < text.index("$    35,000.00")

print("Strategy ordering verification passed.")

print()
print("All withdrawal strategy comparison report tests passed.")
