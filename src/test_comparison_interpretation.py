from investment_analyzer.analysis.portfolio_comparator import PortfolioComparator
from investment_analyzer.models.portfolio import Portfolio

portfolio_a = Portfolio("Current Allocation")

portfolio_a.add_fund("VWENX", 40)
portfolio_a.add_fund("VGSTX", 30)
portfolio_a.add_fund("VBIAX", 20)
portfolio_a.add_fund("VSMGX", 10)


portfolio_b = Portfolio("Equal Allocation")

portfolio_b.add_fund("VWENX", 25)
portfolio_b.add_fund("VGSTX", 25)
portfolio_b.add_fund("VBIAX", 25)
portfolio_b.add_fund("VSMGX", 25)


comparator = PortfolioComparator(
    portfolio_a,
    portfolio_b,
)

interpretation = comparator.interpretation()

print()
print("PORTFOLIO COMPARISON INTERPRETATION")
print("=" * 60)

print()
print("Growth:")
print(interpretation["growth"])

print()
print("Risk:")
print(interpretation["risk"])

print()
print("Drawdown:")
print(interpretation["drawdown"])

print()
print("Risk-Adjusted Performance:")
print(interpretation["risk_adjusted"])

print()
print("Growth of $10,000:")
print(interpretation["ending_value"])
