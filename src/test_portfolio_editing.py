from investment_analyzer.models.portfolio import Portfolio


print()
print("PORTFOLIO EDITING TEST")
print("=" * 60)

portfolio = Portfolio("Version 4.2 Editing Test")

portfolio.add_fund("VBIAX", 50.0)
portfolio.add_fund("VWENX", 30.0)
portfolio.add_fund("VGSTX", 20.0)

assert portfolio.number_of_holdings == 3
assert abs(portfolio.total_allocation - 100.0) < 0.01
assert portfolio.validate()

print("Initial portfolio creation passed.")


# Update allocation
portfolio.update_allocation("VBIAX", 40.0)
portfolio.update_allocation("VWENX", 40.0)

assert abs(portfolio.total_allocation - 100.0) < 0.01
assert portfolio.validate()

print("Allocation update passed.")


# Remove a fund
portfolio.remove_fund("VGSTX")

assert portfolio.number_of_holdings == 2
assert abs(portfolio.total_allocation - 80.0) < 0.01

print("Fund removal passed.")


# Add a replacement fund
portfolio.add_fund("VSMGX", 20.0)

assert portfolio.number_of_holdings == 3
assert abs(portfolio.total_allocation - 100.0) < 0.01
assert portfolio.validate()

print("Fund addition passed.")


# Duplicate fund must fail
try:
    portfolio.add_fund("VBIAX", 10.0)
except ValueError:
    print("Duplicate-fund protection passed.")
else:
    raise AssertionError("Duplicate fund was incorrectly accepted.")


# Invalid allocation must fail
try:
    portfolio.update_allocation("VWENX", 0.0)
except ValueError:
    print("Invalid-allocation protection passed.")
else:
    raise AssertionError("Zero allocation was incorrectly accepted.")


# Updating a missing fund must fail
try:
    portfolio.update_allocation("VTTVX", 10.0)
except ValueError:
    print("Missing-fund update protection passed.")
else:
    raise AssertionError("Missing fund update was incorrectly accepted.")


# Removing a missing fund must fail
try:
    portfolio.remove_fund("VTTVX")
except ValueError:
    print("Missing-fund removal protection passed.")
else:
    raise AssertionError("Missing fund removal was incorrectly accepted.")


print()
portfolio.summary()

print()
print("All portfolio editing tests passed.")
