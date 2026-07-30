from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.reports.report_manager import ReportManager

portfolio = Portfolio("Retirement Portfolio")

portfolio.add_fund("VWENX", 40)
portfolio.add_fund("VGSTX", 30)
portfolio.add_fund("VBIAX", 20)
portfolio.add_fund("VSMGX", 10)

manager = ReportManager()

filename = manager.create_portfolio_report(portfolio)

print()
print("Report created:")
print(filename)
