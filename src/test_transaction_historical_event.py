from datetime import date

from investment_analyzer.models.transaction import (
    Transaction,
    TransactionAction,
)


def test_share_affecting_actions():
    test_cases = [
        (TransactionAction.BUY, "BUY"),
        (TransactionAction.SELL, "SELL"),
        (TransactionAction.REINVEST_DIVIDEND, "REINVEST"),
        (TransactionAction.REINVEST_CAPITAL_GAIN, "REINVEST"),
        (TransactionAction.ADD_SHARES, "ADD"),
        (TransactionAction.REMOVE_SHARES, "REMOVE"),
    ]

    for action, expected_event_type in test_cases:
        transaction = Transaction(
            date=date(2026, 9, 5),
            symbol="VGHAX",
            action=action,
            shares=100.0,
            price=85.50,
            amount=8550.00,
            note="Test transaction",
        )

        event = transaction.to_historical_event()

        assert event.date == date(2026, 9, 5)
        assert event.symbol == "VGHAX"
        assert event.event_type == expected_event_type
        assert event.shares == 100.0
        assert event.price == 85.50
        assert event.amount == 8550.00
        assert event.note == "Test transaction"


def test_cash_only_actions_rejected():
    cash_only_actions = [
        TransactionAction.DIVIDEND,
        TransactionAction.CAPITAL_GAIN,
        TransactionAction.MANAGEMENT_FEE,
    ]

    for action in cash_only_actions:
        transaction = Transaction(
            date=date(2026, 9, 5),
            symbol="VGHAX",
            action=action,
            shares=0.0,
            price=0.0,
            amount=100.00,
        )

        try:
            transaction.to_historical_event()
        except ValueError:
            pass
        else:
            raise AssertionError(
                f"{action} should not convert to a historical share event."
            )


def main():
    test_share_affecting_actions()
    test_cash_only_actions_rejected()

    print("Transaction to historical event tests PASSED.")


if __name__ == "__main__":
    main()
