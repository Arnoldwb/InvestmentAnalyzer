from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)

portfolio.add_fund("VGSTX", 30)

portfolio.add_fund("VBIAX", 20)

portfolio.add_fund("VSMGX", 10)

print()

print("VERIFY PORTFOLIO RETURN CALCULATION")

print("=" * 60)

weighted_total = 0.0

for holding in portfolio.holdings:

    fund = holding.fund

    fund.load_data()

    returns = fund.monthly_returns()

    june_2001 = returns.loc["2001-06-30"]

    weight = holding.allocation / 100.0

    contribution = june_2001 * weight

    weighted_total += contribution

    print()

    print(f"{fund.symbol}")

    print(f"  Allocation   : {holding.allocation:.1f}%")

    print(f"  June Return  : {june_2001:.6f}")

    print(f"  Contribution : {contribution:.6f}")

print()

print("-" * 60)

print(f"Portfolio Return: {weighted_total:.6f}")

print(f"Portfolio Return: {weighted_total:.4%}")
