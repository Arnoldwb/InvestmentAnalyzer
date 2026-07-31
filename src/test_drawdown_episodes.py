from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

analyzer = PortfolioAnalyzer(portfolio)

episodes = analyzer.drawdown_episodes()

print()
print("PORTFOLIO DRAWDOWN EPISODES")
print("=" * 78)

print()
print("Completed episodes:", len(episodes))

print()
print(
    f"{'Peak':<12}"
    f"{'Bottom':<12}"
    f"{'Recovery':<12}"
    f"{'Decline':>12}"
    f"{'Days':>10}"
)

print("-" * 58)

for episode in episodes:
    print(
        f"{episode['peak_date'].date()!s:<12}"
        f"{episode['bottom_date'].date()!s:<12}"
        f"{episode['recovery_date'].date()!s:<12}"
        f"{episode['decline']:>12.2%}"
        f"{episode['days_to_recovery']:>10}"
    )
