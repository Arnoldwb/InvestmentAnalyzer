from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = PortfolioAnalyzer(portfolio)

interpretation = analyzer.stress_interpretation()

print()
print("HISTORICAL STRESS INTERPRETATION")
print("=" * 60)
print()

for text in interpretation.values():
    print(text)
    print()
