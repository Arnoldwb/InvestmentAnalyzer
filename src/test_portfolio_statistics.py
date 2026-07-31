from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = PortfolioAnalyzer(portfolio)

print()
print("PORTFOLIO PERFORMANCE STATISTICS")
print("=" * 60)

print(f"CAGR                  : {analyzer.cagr():.2%}")
print(f"Annualized Avg Return : {analyzer.annualized_return():.2%}")
print(f"Annualized Volatility : {analyzer.annualized_volatility():.2%}")
print(f"Maximum Drawdown      : {analyzer.max_drawdown():.2%}")
print(f"Sharpe Ratio          : {analyzer.sharpe_ratio():.2f}")
print()
print("Growth of $10,000")
print("-" * 60)

growth = analyzer.growth_index(10000)

print("Beginning Value : $10,000.00")
print(f"Ending Value    : ${growth.iloc[-1]:,.2f}")
print(f"Months          : {len(growth)}")
