from pathlib import Path

from investment_analyzer.models.fund import Fund
from investment_analyzer.analysis.cycle_analyzer import MarketCycleAnalyzer
from investment_analyzer.reports.excel_report import ExcelReport


report = ExcelReport()

project_root = Path(__file__).resolve().parents[1]
data_folder = project_root / "data"

csv_files = sorted(data_folder.glob("*.csv"))

print()
print("Creating Excel report...")
print()

for csv_file in csv_files:

    symbol = csv_file.stem

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