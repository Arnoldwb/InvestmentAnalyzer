from investment_analyzer.models.fund import Fund
from investment_analyzer.analysis.cycle_analyzer import MarketCycleAnalyzer

fund = Fund("VWENX").load_data()

analyzer = MarketCycleAnalyzer(fund)
cycles = analyzer.build_cycles()

print()
print("=" * 90)
print(f"Market Cycle Report for {fund.symbol}")
print("=" * 90)

print(
    f"{'#':>3} "
    f"{'Type':<6} "
    f"{'Start':<12} "
    f"{'End':<12} "
    f"{'Days':>6} "
    f"{'Return %':>10}"
)

print("-" * 90)

bull_returns = []
bear_returns = []

longest_bull = None
longest_bear = None

for i, cycle in enumerate(cycles, start=1):

    print(
        f"{i:>3} "
        f"{cycle.cycle_type:<6} "
        f"{str(cycle.start_date.date()):<12} "
        f"{str(cycle.end_date.date()):<12} "
        f"{cycle.days:>6} "
        f"{cycle.percent_change:>10.2f}"
    )

    if cycle.cycle_type == "Bull":
        bull_returns.append(cycle.percent_change)
        if longest_bull is None or cycle.days > longest_bull.days:
            longest_bull = cycle
    else:
        bear_returns.append(cycle.percent_change)
        if longest_bear is None or cycle.days > longest_bear.days:
            longest_bear = cycle

print()
print("=" * 90)
print(f"Total Cycles : {len(cycles)}")
print(f"Bull Markets : {len(bull_returns)}")
print(f"Bear Markets : {len(bear_returns)}")
print()

if bull_returns:
    print(f"Average Bull Return : {sum(bull_returns)/len(bull_returns):8.2f}%")

if bear_returns:
    print(f"Average Bear Return : {sum(bear_returns)/len(bear_returns):8.2f}%")

print()

if longest_bull:
    print(
        f"Longest Bull : {longest_bull.days} days "
        f"({longest_bull.start_date.date()} -> {longest_bull.end_date.date()})"
    )

if longest_bear:
    print(
        f"Longest Bear : {longest_bear.days} days "
        f"({longest_bear.start_date.date()} -> {longest_bear.end_date.date()})"
    )

print("=" * 90)