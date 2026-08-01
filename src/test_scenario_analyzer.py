from investment_analyzer.analysis.scenario_analyzer import ScenarioAnalyzer
from investment_analyzer.models.portfolio import Portfolio


portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = ScenarioAnalyzer(portfolio)

result = analyzer.analyze_period(
    "2008-01-01",
    "2009-12-31",
)

print()
print("HISTORICAL SCENARIO ANALYSIS")
print("=" * 60)

print()
print("Requested Period:  January 2008 through December 2009")
print()

print(f"Data Start:        {result['start_date'].strftime('%B %Y')}")
print(f"Data End:          {result['end_date'].strftime('%B %Y')}")
print(f"Months:            {result['months']}")
print(f"Total Return:      {result['total_return']:.2%}")
print(f"Maximum Drawdown:  {result['max_drawdown']:.2%}")
