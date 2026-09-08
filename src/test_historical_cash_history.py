from datetime import date

from investment_analyzer.core.historical_cash_history import (
    reconstruct_cash_history,
)
from investment_analyzer.models.historical_starting_cash import (
    HistoricalStartingCash,
)
from investment_analyzer.models.transaction import Transaction, TransactionAction


starting_cash = HistoricalStartingCash(
    date=date(2020, 1, 1),
    amount=10000.00,
    source="Test statement",
)

transactions = [
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

history = reconstruct_cash_history(starting_cash, transactions)

expected = [10000.00, 8000.00, 8100.00, 9350.00, 9350.00, 8350.00]

assert history["Cash"].tolist() == expected
assert len(history) == 6

print("Historical cash history test PASSED.")
print(history.to_string(index=False))
