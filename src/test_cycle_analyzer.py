from investment_analyzer.models.fund import Fund
from investment_analyzer.analysis.cycle_analyzer import MarketCycleAnalyzer


fund = Fund("VWENX").load_data()

analyzer = MarketCycleAnalyzer(fund)

cycles = analyzer.build_cycles()

print()
print(f"Detected {len(cycles)} market cycles")
print("-" * 70)

for cycle in cycles[:10]:
    print(
        f"{cycle.cycle_type:5} "
        f"{cycle.start_date.date()}  ->  "
        f"{cycle.end_date.date()}   "
        f"{cycle.percent_change:7.2f}%   "
        f"{cycle.days:5} days"
    )