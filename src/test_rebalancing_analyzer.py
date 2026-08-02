from investment_analyzer.analysis.rebalancing_analyzer import RebalancingAnalyzer
from investment_analyzer.models.portfolio import Portfolio


print()
print("REBALANCING ANALYZER TEST")
print("=" * 60)

current = Portfolio("Current Portfolio")
current.add_fund("VBIAX", 50.0)
current.add_fund("VWENX", 30.0)
current.add_fund("VSMGX", 20.0)
current.validate()

proposed = Portfolio("Proposed Portfolio")
proposed.add_fund("VBIAX", 40.0)
proposed.add_fund("VWENX", 35.0)
proposed.add_fund("VGSTX", 25.0)
proposed.validate()

analyzer = RebalancingAnalyzer(current, proposed)
changes = analyzer.allocation_changes()

expected = {
    "VBIAX": (50.0, 40.0, -10.0),
    "VGSTX": (0.0, 25.0, 25.0),
    "VSMGX": (20.0, 0.0, -20.0),
    "VWENX": (30.0, 35.0, 5.0),
}

assert len(changes) == 4

for item in changes:
    symbol = item["symbol"]

    assert symbol in expected

    current_expected, proposed_expected, change_expected = expected[symbol]

    assert item["current"] == current_expected
    assert item["proposed"] == proposed_expected
    assert item["change"] == change_expected

print("Allocation change calculations passed.")
print("Added-fund handling passed.")
print("Removed-fund handling passed.")

total_current = sum(item["current"] for item in changes)
total_proposed = sum(item["proposed"] for item in changes)
total_change = sum(item["change"] for item in changes)

assert abs(total_current - 100.0) < 0.01
assert abs(total_proposed - 100.0) < 0.01
assert abs(total_change) < 0.01

print("Allocation totals verification passed.")

print()
print("Calculated changes:")
print("-" * 60)

for item in changes:
    print(
        f"{item['symbol']:8}"
        f"{item['current']:8.1f}%"
        f"{item['proposed']:10.1f}%"
        f"{item['change']:+10.1f}%"
    )

print()
print("All rebalancing analyzer tests passed.")

print()
print("DOLLAR REBALANCING TEST")
print("=" * 60)

portfolio_value = 500000.0
dollar_changes = analyzer.dollar_changes(portfolio_value)

expected_dollars = {
    "VBIAX": (250000.0, 200000.0, -50000.0),
    "VGSTX": (0.0, 125000.0, 125000.0),
    "VSMGX": (100000.0, 0.0, -100000.0),
    "VWENX": (150000.0, 175000.0, 25000.0),
}

for item in dollar_changes:
    symbol = item["symbol"]

    current_expected, proposed_expected, change_expected = (
        expected_dollars[symbol]
    )

    assert abs(
        item["current_value"] - current_expected
    ) < 0.01

    assert abs(
        item["proposed_value"] - proposed_expected
    ) < 0.01

    assert abs(
        item["dollar_change"] - change_expected
    ) < 0.01

print("Dollar change calculations passed.")

total_sales = sum(
    -item["dollar_change"]
    for item in dollar_changes
    if item["dollar_change"] < 0
)

total_purchases = sum(
    item["dollar_change"]
    for item in dollar_changes
    if item["dollar_change"] > 0
)

assert abs(total_sales - 150000.0) < 0.01
assert abs(total_purchases - 150000.0) < 0.01
assert abs(total_sales - total_purchases) < 0.01

print("Buy/sell balance verification passed.")

try:
    analyzer.dollar_changes(0)
except ValueError:
    print("Invalid portfolio value protection passed.")
else:
    raise AssertionError(
        "Zero portfolio value should raise ValueError."
    )

print()
print("Dollar changes:")
print("-" * 78)

for item in dollar_changes:
    print(
        f"{item['symbol']:8}"
        f"${item['current_value']:>12,.2f}"
        f"${item['proposed_value']:>12,.2f}"
        f"{item['dollar_change']:>+14,.2f}"
    )

print("-" * 78)
print(f"Total sales:     ${total_sales:,.2f}")
print(f"Total purchases: ${total_purchases:,.2f}")

print()
print("All dollar rebalancing tests passed.")
