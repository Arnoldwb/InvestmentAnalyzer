from datetime import date

from investment_analyzer.models.historical_starting_cash import (
    HistoricalStartingCash,
)
from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.models.transaction import Transaction, TransactionAction


portfolio = Portfolio("Portfolio Cash History Test")

portfolio.add_fund("VBIAX", 100.0)

portfolio.historical_starting_cash = HistoricalStartingCash(
    date=date(2020, 1, 1),
    amount=10000.00,
)

portfolio.transactions.extend(
    [
        Transaction(
            date=date(2020, 1, 5),
            symbol="VBIAX",
            action=TransactionAction.BUY,
            shares=100,
            price=20,
        ),
        Transaction(
            date=date(2020, 1, 10),
            symbol="VBIAX",
            action=TransactionAction.DIVIDEND,
            shares=0,
            price=0,
            amount=100,
        ),
        Transaction(
            date=date(2020, 1, 15),
            symbol="VBIAX",
            action=TransactionAction.SELL,
            shares=50,
            price=25,
        ),
        Transaction(
            date=date(2020, 1, 20),
            symbol="VBIAX",
            action=TransactionAction.REINVEST_DIVIDEND,
            shares=5,
            price=20,
        ),
        Transaction(
            date=date(2020, 1, 25),
            symbol="",
            action=TransactionAction.WITHDRAWAL,
            shares=0,
            price=0,
            amount=1000,
        ),
    ]
)

history = portfolio.historical_cash_history()

expected = [10000.00, 8000.00, 8100.00, 9350.00, 9350.00, 8350.00]

assert history["Cash"].tolist() == expected
assert len(history) == 6

print("Portfolio historical cash history test PASSED.")
print(history.to_string(index=False))
