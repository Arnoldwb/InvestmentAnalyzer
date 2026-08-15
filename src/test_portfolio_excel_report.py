from investment_analyzer.core.portfolio_storage import (
    load_portfolio,
)
from investment_analyzer.reports.portfolio_excel_report import (
    PortfolioExcelReport,
)

portfolio = load_portfolio("Test_Portfolio.json")

report = PortfolioExcelReport()

output = report.create_portfolio_report(portfolio)

print()
print("Portfolio Excel report created:")
print(output)
