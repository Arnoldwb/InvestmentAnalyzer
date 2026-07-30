from investment_analyzer.models.portfolio import Portfolio

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)

portfolio.add_fund("VGSTX", 30)

portfolio.add_fund("VBIAX", 20)

portfolio.add_fund("VSMGX", 10)

portfolio.summary()

portfolio.validate()

print()

print("Portfolio validation successful.")