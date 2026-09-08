from investment_analyzer.models.historical_starting_cash import (
    HistoricalStartingCash,
)
from investment_analyzer.models.transaction import Transaction, TransactionAction


def transaction_cash_effect(transaction: Transaction) -> float:
    """
    Return the cash effect caused by one transaction.

    Positive values increase cash.
    Negative values decrease cash.
    Zero means the transaction does not affect cash.
    """

    action = transaction.action.upper()

    if action == TransactionAction.BUY:
        return -(transaction.shares * transaction.price)

    if action == TransactionAction.SELL:
        return transaction.shares * transaction.price

    if action in {
        TransactionAction.DIVIDEND,
        TransactionAction.CAPITAL_GAIN,
        TransactionAction.DEPOSIT,
        TransactionAction.CASH_INTEREST,
        TransactionAction.CASH_ADJUSTMENT,
    }:
        return transaction.amount

    if action in {
        TransactionAction.WITHDRAWAL,
        TransactionAction.MANAGEMENT_FEE,
    }:
        return -transaction.amount

    if action in {
        TransactionAction.REINVEST_DIVIDEND,
        TransactionAction.REINVEST_CAPITAL_GAIN,
        TransactionAction.ADD_SHARES,
        TransactionAction.REMOVE_SHARES,
    }:
        return 0.0

    raise ValueError(f"Unsupported transaction action: {action}")


def reconstruct_cash_history(
    starting_cash: HistoricalStartingCash,
    transactions: list[Transaction],
):
    """
    Reconstruct the chronological cash balance of a portfolio.

    Starting cash establishes the opening balance.
    Transactions then modify the balance chronologically.

    Returns a DataFrame with one row for each date at which
    the cash balance is established or changed.
    """

    import pandas as pd

    cash = starting_cash.amount
    rows = [
        {
            "Date": starting_cash.date,
            "Cash": cash,
        }
    ]

    for transaction in sorted(transactions, key=lambda transaction: transaction.date):
        cash += transaction_cash_effect(transaction)

        rows.append(
            {
                "Date": transaction.date,
                "Cash": cash,
            }
        )

    history = pd.DataFrame(rows)

    history["Date"] = pd.to_datetime(history["Date"])

    return history.sort_values("Date").reset_index(drop=True)
