from investment_analyzer.core.file_discovery import discover_funds

funds = discover_funds()

print("\nFunds discovered:\n")

for fund in funds:
    print(f"  {fund}")