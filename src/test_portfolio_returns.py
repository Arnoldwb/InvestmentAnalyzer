from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = PortfolioAnalyzer(portfolio)

returns = analyzer.monthly_returns()

print()
print("PORTFOLIO MONTHLY RETURNS")
print("=" * 50)

print()
print("Number of months:", len(returns))

print()
print("First 5 months:")
print(returns.head())

print()
print("Last 5 months:")
print(returns.tail())

print()
print("First month:", returns.index.min())
print("Last month :", returns.index.max())
