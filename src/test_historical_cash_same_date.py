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
    amount=5000.00,
)

transactions = [
    Transaction(
        date=date(2020, 1, 5),
        symbol="VBIAX",
        action=TransactionAction.BUY,
        shares=50,
        price=20,
    ),
    Transaction(
        date=date(2020, 1, 5),
        symbol="VBIAX",
        action=TransactionAction.DIVIDEND,
        shares=0,
        price=0,
        amount=100,
    ),
]

history = reconstruct_cash_history(starting_cash, transactions)

assert history.iloc[-1]["Cash"] == 4100.00
assert len(history) == 3

print("Historical cash same-date test PASSED.")
print(history.to_string(index=False))
