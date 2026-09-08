from datetime import date

from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.models.transaction import Transaction, TransactionAction


def main():
    portfolio = Portfolio(name="Cash Transaction Test")

    portfolio.add_fund(
        symbol="VWENX",
        allocation=100.0,
        shares=100.0,
    )

    deposit = Transaction(
        date=date(2026, 1, 1),
        symbol="",
        action=TransactionAction.DEPOSIT,
        shares=0.0,
        price=0.0,
        amount=1000.0,
        note="Test deposit",
    )

    portfolio.add_transaction(deposit)

    assert len(portfolio.transactions) == 1
    assert portfolio.transactions[0].action == TransactionAction.DEPOSIT
    assert portfolio.transactions[0].symbol == ""
    assert portfolio.holdings[0].shares == 100.0

    withdrawal = Transaction(
        date=date(2026, 1, 2),
        symbol="",
        action=TransactionAction.WITHDRAWAL,
        shares=0.0,
        price=0.0,
        amount=250.0,
        note="Test withdrawal",
    )

    portfolio.add_transaction(withdrawal)

    assert len(portfolio.transactions) == 2
    assert portfolio.holdings[0].shares == 100.0

    print("Portfolio cash transaction test PASSED.")
    print()
    print("Transactions:", len(portfolio.transactions))
    print("Holding shares:", portfolio.holdings[0].shares)


if __name__ == "__main__":
    main()
