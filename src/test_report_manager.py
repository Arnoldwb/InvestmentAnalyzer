from investment_analyzer.reports.report_manager import ReportManager

manager = ReportManager()

print("Reports folder:")
print(manager.output_folder)

print()

print("Sample report path:")
print(manager.report_path("PortfolioReport.txt"))
