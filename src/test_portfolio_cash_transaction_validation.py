from datetime import date

from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.models.transaction import Transaction, TransactionAction


def make_portfolio():
    portfolio = Portfolio(name="Cash Validation Test")

    portfolio.add_fund(
        symbol="VWENX",
        allocation=100.0,
        shares=100.0,
    )

    return portfolio


def expect_error(portfolio, transaction, expected_text):
    try:
        portfolio.add_transaction(transaction)
    except ValueError as error:
        assert expected_text in str(error)
        return

    raise AssertionError(f"Expected ValueError containing '{expected_text}'.")


def main():
    # Cash transaction with nonzero shares.
    portfolio = make_portfolio()

    transaction = Transaction(
        date=date(2026, 1, 1),
        symbol="",
        action=TransactionAction.DEPOSIT,
        shares=10.0,
        price=0.0,
        amount=1000.0,
    )

    expect_error(
        portfolio,
        transaction,
        "DEPOSIT must have zero shares.",
    )

    # Cash transaction with nonzero price.
    portfolio = make_portfolio()

    transaction = Transaction(
        date=date(2026, 1, 1),
        symbol="",
        action=TransactionAction.DEPOSIT,
        shares=0.0,
        price=10.0,
        amount=1000.0,
    )

    expect_error(
        portfolio,
        transaction,
        "DEPOSIT must have zero price.",
    )

    # Cash transaction with zero amount.
    portfolio = make_portfolio()

    transaction = Transaction(
        date=date(2026, 1, 1),
        symbol="",
        action=TransactionAction.DEPOSIT,
        shares=0.0,
        price=0.0,
        amount=0.0,
    )

    expect_error(
        portfolio,
        transaction,
        "DEPOSIT must have a positive amount.",
    )

    # Cash transaction with negative amount.
    portfolio = make_portfolio()

    transaction = Transaction(
        date=date(2026, 1, 1),
        symbol="",
        action=TransactionAction.DEPOSIT,
        shares=0.0,
        price=0.0,
        amount=-100.0,
    )

    expect_error(
        portfolio,
        transaction,
        "DEPOSIT must have a positive amount.",
    )

    print("Portfolio cash transaction validation test PASSED.")


if __name__ == "__main__":
    main()
