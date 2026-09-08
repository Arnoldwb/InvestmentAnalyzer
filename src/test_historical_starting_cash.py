from datetime import date

from investment_analyzer.models.historical_starting_cash import (
    HistoricalStartingCash,
)
from investment_analyzer.models.portfolio import Portfolio


portfolio = Portfolio("Cash Test")

starting_cash = HistoricalStartingCash(
    date=date(2020, 1, 1),
    amount=25000.00,
    source="Test statement",
)

portfolio.historical_starting_cash = starting_cash

assert portfolio.historical_starting_cash is not None
assert portfolio.historical_starting_cash.date == date(2020, 1, 1)
assert portfolio.historical_starting_cash.amount == 25000.00
assert portfolio.historical_starting_cash.source == "Test statement"

print("Historical starting cash test PASSED.")
