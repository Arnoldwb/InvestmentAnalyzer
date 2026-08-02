from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.analysis.portfolio_comparator import PortfolioComparator


print()
print("PORTFOLIO REBALANCING TEST")
print("=" * 60)

# Current portfolio
current = Portfolio("Current Portfolio")
current.add_fund("VBIAX", 50.0)
current.add_fund("VWENX", 50.0)
current.validate()

# Proposed rebalanced portfolio
proposed = Portfolio("Proposed Portfolio")
proposed.add_fund("VBIAX", 50.0)
proposed.add_fund("VWENX", 30.0)
proposed.add_fund("VGSTX", 20.0)
proposed.validate()

# Verify current portfolio remains unchanged
current_allocations = {
    holding.fund.symbol: holding.allocation
    for holding in current.holdings
}

assert current_allocations == {
    "VBIAX": 50.0,
    "VWENX": 50.0,
}

print("Original portfolio protection passed.")

# Verify proposed allocation
proposed_allocations = {
    holding.fund.symbol: holding.allocation
    for holding in proposed.holdings
}

assert proposed_allocations == {
    "VBIAX": 50.0,
    "VWENX": 30.0,
    "VGSTX": 20.0,
}

print("Proposed allocation verification passed.")

# Verify portfolios can be compared
comparator = PortfolioComparator(current, proposed)
results = comparator.compare()

assert results["portfolio_a"]["name"] == "Current Portfolio"
assert results["portfolio_b"]["name"] == "Proposed Portfolio"

for key in (
    "cagr",
    "annualized_return",
    "volatility",
    "max_drawdown",
    "sharpe",
    "ending_value",
):
    assert key in results["portfolio_a"]
    assert key in results["portfolio_b"]

print("Portfolio comparison verification passed.")

# Verify comparison did not mutate either portfolio
assert current_allocations == {
    holding.fund.symbol: holding.allocation
    for holding in current.holdings
}

assert proposed_allocations == {
    holding.fund.symbol: holding.allocation
    for holding in proposed.holdings
}

print("Non-destructive comparison verification passed.")

print()
print("All portfolio rebalancing tests passed.")
