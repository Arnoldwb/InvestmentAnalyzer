from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = PortfolioAnalyzer(portfolio)

episodes = analyzer.major_drawdowns(threshold=0.10)

print()
print("MAJOR PORTFOLIO DRAWDOWNS")
print("=" * 82)

print()
print("Threshold: 10%")
print("Major drawdowns:", len(episodes))

print()

print(
    f"{'Peak':<12}"
    f"{'Bottom':<12}"
    f"{'Recovery':<12}"
    f"{'Decline':>10}"
    f"{'To Bottom':>12}"
    f"{'Bottom-Recovery':>18}"
    f"{'Total Recovery':>16}"
)

print("-" * 92)

for episode in episodes:
    print(
        f"{episode['peak_date'].date()!s:<12}"
        f"{episode['bottom_date'].date()!s:<12}"
        f"{episode['recovery_date'].date()!s:<12}"
        f"{episode['decline']:>10.2%}"
        f"{episode['days_to_bottom']:>12}"
        f"{episode['days_bottom_to_recovery']:>18}"
        f"{episode['days_to_recovery']:>16}"
    )
