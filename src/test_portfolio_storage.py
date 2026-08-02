from investment_analyzer.core.portfolio_storage import (
    delete_portfolio,
    load_portfolio,
    rename_portfolio,
    save_portfolio,
)
from investment_analyzer.models.portfolio import Portfolio


TEST_NAME = "Version 4.1 Storage Test"
RENAMED_NAME = "Version 4.1 Renamed Test"


portfolio = Portfolio(TEST_NAME)
portfolio.add_fund("VBIAX", 60.0)
portfolio.add_fund("VWENX", 40.0)

print()
print("PORTFOLIO STORAGE TEST")
print("=" * 60)

# Save
saved_path = save_portfolio(portfolio)
print("Saved:")
print(saved_path)

# Load
loaded = load_portfolio(saved_path.name)

assert loaded.name == TEST_NAME
assert loaded.number_of_holdings == 2
assert abs(loaded.total_allocation - 100.0) < 0.01

print()
print("Load test passed.")

# Rename
renamed_path = rename_portfolio(
    saved_path.name,
    RENAMED_NAME,
)

assert not saved_path.exists()
assert renamed_path.exists()

renamed = load_portfolio(renamed_path.name)

assert renamed.name == RENAMED_NAME
assert renamed.number_of_holdings == 2
assert abs(renamed.total_allocation - 100.0) < 0.01

print("Rename test passed.")

# Delete
deleted_path = delete_portfolio(renamed_path.name)

assert not deleted_path.exists()

print("Delete test passed.")

print()
print("All portfolio storage tests passed.")
