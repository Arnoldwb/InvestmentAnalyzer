from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = PortfolioAnalyzer(portfolio)

drawdowns = analyzer.drawdown_series()

print()
print("PORTFOLIO DRAWDOWN SERIES")
print("=" * 60)

print()
print("Number of months:", len(drawdowns))

print()
print("First 5 months:")
print(drawdowns.head())

print()
print("Worst 10 months:")
print(drawdowns.nsmallest(10))

print()
print("Maximum Drawdown:")
print(f"{analyzer.max_drawdown():.2%}")
