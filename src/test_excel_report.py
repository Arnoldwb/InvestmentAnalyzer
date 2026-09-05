from investment_analyzer.models.fund import Fund
from investment_analyzer.analysis.cycle_analyzer import MarketCycleAnalyzer
from investment_analyzer.reports.excel_report import ExcelReport
from investment_analyzer.core.file_discovery import discover_funds

report = ExcelReport()

print()
print("Creating Excel report...")
print()

funds = discover_funds()

for symbol in funds:

    print(f"Processing {symbol}...")

    fund = Fund(symbol).load_data()

    analyzer = MarketCycleAnalyzer(fund)

    cycles = analyzer.build_cycles()

    report.add_fund(symbol, cycles)

output = report.save()

print()
print("Done.")
print(f"Workbook written to:")
print(output)
