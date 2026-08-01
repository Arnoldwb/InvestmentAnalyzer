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
print("HISTORICAL STRESS AND RECOVERY")
print("=" * 60)

for scenario in HISTORICAL_SCENARIOS.values():

    result = analyzer.recovery_analysis(
        scenario["start_date"],
        scenario["end_date"],
    )

    print()
    print(scenario["name"])
    print("-" * 60)

    print(
        f"Peak:                "
        f"{result['peak_date'].strftime('%B %Y')}"
    )

    print(
        f"Bottom:              "
        f"{result['bottom_date'].strftime('%B %Y')}"
    )

    print(f"Maximum Decline:     {result['decline']:.2%}")
    print(f"Peak to Bottom:      {result['days_to_bottom']:,} days")

    if result["recovery_date"] is not None:

        print(
            f"Full Recovery:       "
            f"{result['recovery_date'].strftime('%B %Y')}"
        )

        print(
            f"Bottom to Recovery:  "
            f"{result['days_bottom_to_recovery']:,} days"
        )

        print(
            f"Peak to Recovery:    "
            f"{result['days_to_recovery']:,} days"
        )

    else:
        print("Full Recovery:       Not reached in available data")
