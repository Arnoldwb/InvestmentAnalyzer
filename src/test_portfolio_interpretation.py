from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = PortfolioAnalyzer(portfolio)

interpretation = analyzer.interpretation()

print()
print("PORTFOLIO INTERPRETATION")
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
