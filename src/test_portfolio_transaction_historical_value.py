from datetime import date

import pandas as pd

from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.models.transaction import Transaction, TransactionAction
from investment_analyzer.models.holding import Holding
from investment_analyzer.models.fund import Fund
from investment_analyzer.models.historical_starting_position import (
    HistoricalStartingPosition,
)


def main():
    portfolio = Portfolio(name="Transaction Historical Value Test")
    fund = Fund("VGHAX")
    fund.load_data()

    portfolio.holdings.append(
        Holding(
            fund=fund,
            allocation=1.0,
            shares=100.0,
        )
    )

    # Establish the historical starting position directly.
    portfolio.historical_starting_positions.append(
        HistoricalStartingPosition(
            symbol="VGHAX",
            shares=100.0,
            date=date(2024, 9, 25),
        )
    )

    # Add transactions, but deliberately do NOT add explicit historical events.
    portfolio.add_transaction(
        Transaction(
            date=date(2024, 10, 1),
            symbol="VGHAX",
            action=TransactionAction.BUY,
            shares=50.0,
            price=79.93,
        )
    )

    portfolio.add_transaction(
        Transaction(
            date=date(2024, 10, 15),
            symbol="VGHAX",
            action=TransactionAction.SELL,
            shares=20.0,
            price=80.00,
        )
    )

    # Confirm the test is exercising the new fallback path.
    assert portfolio.historical_events == []

    value_history = portfolio.historical_value_history()

    assert not value_history.empty
    assert set(value_history["Symbol"]) == {"VGHAX"}

    # Starting position: 100 shares.
    first = value_history.iloc[0]
    assert first["Shares"] == 100.0

    # After BUY: 150 shares.
    buy_day = value_history[value_history["Date"] == pd.Timestamp("2024-10-01")]
    assert len(buy_day) == 1
    assert buy_day.iloc[0]["Shares"] == 150.0

    # After SELL: 130 shares.
    sell_day = value_history[value_history["Date"] == pd.Timestamp("2024-10-15")]
    assert len(sell_day) == 1
    assert sell_day.iloc[0]["Shares"] == 130.0

    print("Portfolio transaction historical value test PASSED.")
    print("No explicit historical events were supplied.")
    print("Historical value history was successfully generated from transactions.")


if __name__ == "__main__":
    main()
