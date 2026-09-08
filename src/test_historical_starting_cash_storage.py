from datetime import date
from pathlib import Path

from investment_analyzer.core.portfolio_storage import (
    load_portfolio,
    save_portfolio,
)
from investment_analyzer.models.historical_starting_cash import (
    HistoricalStartingCash,
)
from investment_analyzer.models.portfolio import Portfolio


portfolio = Portfolio("Historical Starting Cash Storage Test")
portfolio.add_fund("VBIAX", 100.0)

portfolio.historical_starting_cash = HistoricalStartingCash(
    date=date(2020, 1, 1),
    amount=25000.00,
    source="Test statement",
)

filename = "Historical_Starting_Cash_Test.json"

try:
    path = save_portfolio(portfolio, filename)

    loaded = load_portfolio(filename)

    assert loaded.historical_starting_cash is not None
    assert loaded.historical_starting_cash.date == date(2020, 1, 1)
    assert loaded.historical_starting_cash.amount == 25000.00
    assert loaded.historical_starting_cash.source == "Test statement"

    print("Historical starting cash storage test PASSED.")

finally:
    path = Path("portfolios") / filename

    if path.exists():
        path.unlink()
