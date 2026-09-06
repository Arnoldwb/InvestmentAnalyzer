from datetime import date

from investment_analyzer.core.historical_value_history import (
    calculate_historical_value_history,
)
from investment_analyzer.core.historical_share_history import (
    reconstruct_share_history,
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
            date=date(2024, 9, 25),
            symbol="Vanguard Health Care-Admiral",
            shares=100.0,
            source="Transaction historical value test",
        )
    ]

    transactions = [
        Transaction(
            date=date(2024, 10, 1),
            symbol="Vanguard Health Care-Admiral",
            action=TransactionAction.BUY,
            shares=50.0,
            price=79.93,
            amount=3996.50,
        ),
        Transaction(
            date=date(2024, 10, 15),
            symbol="Vanguard Health Care-Admiral",
            action=TransactionAction.SELL,
            shares=20.0,
            price=80.00,
            amount=1600.00,
        ),
    ]

    historical_events = [
        transaction.to_historical_event() for transaction in transactions
    ]

    share_history = reconstruct_share_history(
        starting_positions,
        historical_events,
    )

    value_history = calculate_historical_value_history(share_history)

    assert not value_history.empty

    first_row = value_history.iloc[0]

    assert first_row["Date"].date() == date(2024, 9, 25)
    assert first_row["Symbol"] == "VGHAX"
    assert first_row["Shares"] == 100.0
    assert first_row["Price"] == 80.40
    assert abs(first_row["Value"] - 8040.00) < 0.01

    buy_day = value_history[value_history["Date"].dt.date == date(2024, 10, 1)].iloc[0]

    assert buy_day["Shares"] == 150.0
    assert buy_day["Price"] == 79.93
    assert abs(buy_day["Value"] - 11989.50) < 0.01

    sell_day = value_history[value_history["Date"].dt.date == date(2024, 10, 15)].iloc[
        0
    ]

    assert sell_day["Shares"] == 130.0

    print("Transaction to historical value test PASSED.")
    print()
    print("Starting position: 100.000 shares")
    print("BUY:                +50.000 shares")
    print("SELL:               -20.000 shares")
    print()
    print(f"Starting value:     ${first_row['Value']:,.2f}")
    print(f"Value on buy date:  ${buy_day['Value']:,.2f}")
    print(f"Shares after sell:  {sell_day['Shares']:.3f}")


if __name__ == "__main__":
    main()
