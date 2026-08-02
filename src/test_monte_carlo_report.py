from investment_analyzer.core.portfolio_storage import load_portfolio
from investment_analyzer.reports.report_manager import ReportManager


print()
print("MONTE CARLO REPORT TEST")
print("=" * 60)

portfolio = load_portfolio("Version_4_Test.json")

manager = ReportManager()

filename = manager.create_monte_carlo_report(
    portfolio=portfolio,
    initial_value=500000.0,
    years=10,
    simulations=10000,
    target_value=1000000.0,
    seed=42,
)

print()
print("Monte Carlo report created:")
print(filename)

assert filename.exists()
print("Report file verification passed.")

text = filename.read_text()

required_text = [
    "Monte Carlo Portfolio Analysis Report",
    "Version 4 Test",
    "$500,000.00",
    "10 years",
    "10,000",
    "$1,000,000.00",
    "10th Percentile",
    "25th Percentile",
    "Median",
    "75th Percentile",
    "90th Percentile",
    "Mean Ending Value",
    "Above Starting Value",
    "At or Above Target",
    "not forecasts or guarantees",
]

for item in required_text:
    assert item in text, (
        f"Expected report text not found: {item}"
    )

print("Report content verification passed.")

# These values come from the fixed-seed Monte Carlo test.
assert "$714,615.60" in text
assert "$1,062,669.93" in text
assert "99.10%" in text
assert "58.05%" in text

print("Fixed-seed result verification passed.")

print()
print("All Monte Carlo report tests passed.")
