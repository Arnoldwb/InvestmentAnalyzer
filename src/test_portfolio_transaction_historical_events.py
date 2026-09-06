from datetime import date

from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.models.transaction import (
    Transaction,
    TransactionAction,
)


def main():
    portfolio = Portfolio(name="Transaction History Test")

    transactions = [
        Transaction(
            date=date(2026, 3, 1),
            symbol="VGHAX",
            action=TransactionAction.SELL,
            shares=20.0,
            price=85.00,
            amount=1700.00,
            note="Test sell",
        ),
        Transaction(
            date=date(2026, 2, 1),
            symbol="VGHAX",
            action=TransactionAction.BUY,
            shares=50.0,
            price=80.00,
            amount=4000.00,
            note="Test buy",
        ),
        Transaction(
            date=date(2026, 4, 1),
            symbol="VGHAX",
            action=TransactionAction.DIVIDEND,
            shares=0.0,
            price=0.0,
            amount=100.00,
            note="Test dividend",
        ),
    ]

    portfolio.transactions.extend(transactions)

    events = portfolio.transaction_historical_events()

    assert len(events) == 2

    assert events[0].date == date(2026, 3, 1)
    assert events[0].symbol == "VGHAX"
    assert events[0].event_type == "SELL"
    assert events[0].shares == 20.0
    assert events[0].price == 85.00
    assert events[0].amount == 1700.00
    assert events[0].note == "Test sell"

    assert events[1].date == date(2026, 2, 1)
    assert events[1].symbol == "VGHAX"
    assert events[1].event_type == "BUY"
    assert events[1].shares == 50.0
    assert events[1].price == 80.00
    assert events[1].amount == 4000.00
    assert events[1].note == "Test buy"

    assert all(
        event.event_type not in {
            "DIVIDEND",
            "CAPITAL GAIN",
            "MANAGEMENT FEE",
        }
        for event in events
    )

    print("Portfolio transaction historical events test PASSED.")
    print()
    print(f"Portfolio transactions: {len(transactions)}")
    print(f"Historical share events: {len(events)}")
    print("Cash-only dividend excluded.")
    print("BUY and SELL converted successfully.")


if __name__ == "__main__":
    main()
