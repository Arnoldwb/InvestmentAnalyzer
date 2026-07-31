from investment_analyzer.analysis.portfolio_comparator import PortfolioComparator
from investment_analyzer.models.portfolio import Portfolio

portfolio_a = Portfolio("Portfolio A - Current Allocation")

portfolio_a.add_fund("VWENX", 40)
portfolio_a.add_fund("VGSTX", 30)
portfolio_a.add_fund("VBIAX", 20)
portfolio_a.add_fund("VSMGX", 10)


portfolio_b = Portfolio("Portfolio B - Equal Allocation")

portfolio_b.add_fund("VWENX", 25)
portfolio_b.add_fund("VGSTX", 25)
portfolio_b.add_fund("VBIAX", 25)
portfolio_b.add_fund("VSMGX", 25)


comparator = PortfolioComparator(
    portfolio_a,
    portfolio_b,
)

results = comparator.compare()

a = results["portfolio_a"]
b = results["portfolio_b"]


print()
print("PORTFOLIO COMPARISON")
print("=" * 78)

print(f"{'Metric':<25}{'Portfolio A':>20}{'Portfolio B':>20}")
print("-" * 78)

print(f"{'CAGR':<25}{a['cagr']:>19.2%}{b['cagr']:>20.2%}")

print(
    f"{'Annualized Avg Return':<25}"
    f"{a['annualized_return']:>19.2%}"
    f"{b['annualized_return']:>20.2%}"
)

print(
    f"{'Annualized Volatility':<25}"
    f"{a['volatility']:>19.2%}"
    f"{b['volatility']:>20.2%}"
)

print(
    f"{'Maximum Drawdown':<25}"
    f"{a['max_drawdown']:>19.2%}"
    f"{b['max_drawdown']:>20.2%}"
)

print(f"{'Sharpe Ratio':<25}" f"{a['sharpe']:>19.2f}" f"{b['sharpe']:>20.2f}")

print()
a_value = f"${a['ending_value']:,.2f}"
b_value = f"${b['ending_value']:,.2f}"

print(f"{'Growth of $10,000':<25}" f"{a_value:>20}" f"{b_value:>20}")
