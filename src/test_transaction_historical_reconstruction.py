from datetime import date

from investment_analyzer.core.historical_reconstruction import (
    reconstruct_shares,
)
from investment_analyzer.models.historical_starting_position import (
    HistoricalStartingPosition,
)
from investment_analyzer.models.transaction import (
    Transaction,
    TransactionAction,
)


def main():
    starting_positions = [
        HistoricalStartingPosition(
            date=date(2026, 1, 1),
            symbol="VGHAX",
            shares=100.0,
            source="Test starting position",
        )
    ]

    transactions = [
        Transaction(
            date=date(2026, 3, 1),
            symbol="VGHAX",
            action=TransactionAction.SELL,
            shares=20.0,
            price=85.00,
            amount=1700.00,
        ),
        Transaction(
            date=date(2026, 2, 1),
            symbol="VGHAX",
            action=TransactionAction.BUY,
            shares=50.0,
            price=80.00,
            amount=4000.00,
        ),
    ]

    historical_events = [
        transaction.to_historical_event()
        for transaction in transactions
    ]

    assert historical_events[0].date == date(2026, 3, 1)
    assert historical_events[1].date == date(2026, 2, 1)

    balances = reconstruct_shares(
        starting_positions,
        historical_events,
    )

    assert balances["VGHAX"] == 130.0

    print("Transaction to historical reconstruction test PASSED.")
    print()
    print("Transactions supplied out of chronological order.")
    print("Historical reconstruction sorts them by date.")
    print()
    print("Starting shares: 100.000")
    print("BUY shares:      +50.000")
    print("SELL shares:     -20.000")
    print(f"Final shares:    {balances['VGHAX']:.3f}")


if __name__ == "__main__":
    main()
