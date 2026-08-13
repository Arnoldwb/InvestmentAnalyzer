from investment_analyzer.core.portfolio_storage import load_portfolio
from investment_analyzer.reports.report_manager import ReportManager


print()
print("SUSTAINABLE WITHDRAWAL REPORT TEST")
print("=" * 60)

portfolio = load_portfolio("Version_4_Test.json")

manager = ReportManager()

filename = manager.create_sustainable_withdrawal_report(
    portfolio=portfolio,
    initial_value=500000.0,
    years=20,
    target_survival_probability=0.90,
    simulations=10000,
    seed=42,
    inflation_rate=0.03,
)

print()
print("Sustainable withdrawal report created:")
print(filename)

assert filename.exists()

print("Report file verification passed.")

text = filename.read_text()

required_text = [
    "Version 5.21",
    "Sustainable Withdrawal Analysis Report",
    "Version 4 Test",
    "$500,000.00",
    "20 years",
    "3.00%",
    "90.00%",
    "10,000",
    "Sustainable Withdrawal",
    "Initial Withdrawal Rate",
    "Actual Survival",
    "VBIAX",
    "VWENX",
    "not a guarantee",
]

for item in required_text:
    assert item in text, (
        f"Expected report text not found: {item}"
    )

print("Report content verification passed.")

assert "$28,823.85" in text
assert "5.76%" in text

print("Fixed-seed result verification passed.")

print()
print("All sustainable withdrawal report tests passed.")
