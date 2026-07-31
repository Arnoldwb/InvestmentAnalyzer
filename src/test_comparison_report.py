from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.reports.report_manager import ReportManager

portfolio_a = Portfolio("Current Allocation")

portfolio_a.add_fund("VWENX", 40)
portfolio_a.add_fund("VGSTX", 30)
portfolio_a.add_fund("VBIAX", 20)
portfolio_a.add_fund("VSMGX", 10)


portfolio_b = Portfolio("Equal Allocation")

portfolio_b.add_fund("VWENX", 25)
portfolio_b.add_fund("VGSTX", 25)
portfolio_b.add_fund("VBIAX", 25)
portfolio_b.add_fund("VSMGX", 25)


manager = ReportManager()

filename = manager.create_comparison_report(
    portfolio_a,
    portfolio_b,
)

print()
print("Comparison report created:")
print(filename)
