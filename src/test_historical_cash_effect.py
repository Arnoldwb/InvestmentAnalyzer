from datetime import date

from investment_analyzer.core.historical_cash_history import (
    transaction_cash_effect,
)
from investment_analyzer.models.transaction import Transaction, TransactionAction


def transaction(action, shares=0.0, price=0.0, amount=0.0):
    return Transaction(
        date=date(2020, 1, 1),
        symbol="VBIAX",
        action=action,
        shares=shares,
        price=price,
        amount=amount,
    )


assert transaction_cash_effect(
    transaction(TransactionAction.BUY, shares=100, price=20)
) == -2000.0

assert transaction_cash_effect(
    transaction(TransactionAction.SELL, shares=25, price=30)
) == 750.0

assert transaction_cash_effect(
    transaction(TransactionAction.DIVIDEND, amount=125)
) == 125.0

assert transaction_cash_effect(
    transaction(TransactionAction.CAPITAL_GAIN, amount=80)
) == 80.0

assert transaction_cash_effect(
    transaction(TransactionAction.MANAGEMENT_FEE, amount=15)
) == -15.0

assert transaction_cash_effect(
    transaction(TransactionAction.DEPOSIT, amount=5000)
) == 5000.0

assert transaction_cash_effect(
    transaction(TransactionAction.WITHDRAWAL, amount=1000)
) == -1000.0

assert transaction_cash_effect(
    transaction(TransactionAction.CASH_INTEREST, amount=20)
) == 20.0

assert transaction_cash_effect(
    transaction(TransactionAction.CASH_ADJUSTMENT, amount=10)
) == 10.0

assert transaction_cash_effect(
    transaction(TransactionAction.REINVEST_DIVIDEND, shares=5, price=20)
) == 0.0

assert transaction_cash_effect(
    transaction(TransactionAction.REINVEST_CAPITAL_GAIN, shares=4, price=20)
) == 0.0

assert transaction_cash_effect(
    transaction(TransactionAction.ADD_SHARES, shares=10, price=20)
) == 0.0

assert transaction_cash_effect(
    transaction(TransactionAction.REMOVE_SHARES, shares=10, price=20)
) == 0.0

print("Historical cash effect test PASSED.")
