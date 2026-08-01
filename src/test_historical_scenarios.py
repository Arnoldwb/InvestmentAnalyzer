from investment_analyzer.analysis.historical_scenarios import HISTORICAL_SCENARIOS
from investment_analyzer.analysis.scenario_analyzer import ScenarioAnalyzer
from investment_analyzer.models.portfolio import Portfolio


portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = ScenarioAnalyzer(portfolio)


print()
print("HISTORICAL STRESS SCENARIOS")
print("=" * 60)

for scenario in HISTORICAL_SCENARIOS.values():

    result = analyzer.analyze_scenario(scenario)

    print()
    print(result["name"])
    print("-" * 60)

    print(
        f"Period:            "
        f"{result['start_date'].strftime('%B %Y')} "
        f"through "
        f"{result['end_date'].strftime('%B %Y')}"
    )

    print(f"Months:            {result['months']}")
    print(f"Total Return:      {result['total_return']:.2%}")
    print(f"Maximum Drawdown:  {result['max_drawdown']:.2%}")

    print()
    print(result["description"])
