from investment_analyzer.importers.vanguard_transaction_importer import (
    VanguardTransactionImporter,
)
from investment_analyzer.models.transaction import TransactionAction


CSV_FILE = "data/Vanguard_Import_09-01-26.csv"


def main():
    transactions = VanguardTransactionImporter.import_file(CSV_FILE)

    assert len(transactions) == 39

    actions = [transaction.action for transaction in transactions]

    assert TransactionAction.BUY in actions
    assert TransactionAction.SELL in actions
    assert TransactionAction.REINVEST_DIVIDEND in actions
    assert TransactionAction.ADD_SHARES in actions
    assert TransactionAction.REMOVE_SHARES in actions
    assert TransactionAction.DIVIDEND in actions
    assert TransactionAction.CAPITAL_GAIN in actions
    assert TransactionAction.WITHDRAWAL in actions

    withdrawals = [
        transaction
        for transaction in transactions
        if transaction.action == TransactionAction.WITHDRAWAL
    ]

    assert len(withdrawals) == 14
    assert all(transaction.symbol == "" for transaction in withdrawals)
    assert all(transaction.shares == 0.0 for transaction in withdrawals)
    assert all(transaction.price == 0.0 for transaction in withdrawals)
    assert all(transaction.amount > 0 for transaction in withdrawals)

    first_buy = next(
        transaction
        for transaction in transactions
        if transaction.action == TransactionAction.BUY
    )

    assert first_buy.symbol == "Vanguard Wellington Admiral"
    assert first_buy.shares == 1384.153
    assert abs(first_buy.price - 81.39998974) < 0.00000001
    assert abs(first_buy.amount - 112670.04) < 0.01

    cash_dividend = next(
        transaction
        for transaction in transactions
        if (
            transaction.action == TransactionAction.DIVIDEND
            and transaction.symbol == ""
        )
    )

    assert cash_dividend.date.isoformat() == "2026-06-22"
    assert abs(cash_dividend.amount - 616.0) < 0.01

    print("Vanguard transaction importer regression test PASSED.")
    print()
    print("Transactions:", len(transactions))
    print("Withdrawals:", len(withdrawals))
    print("Account-level dividend:", cash_dividend.amount)


if __name__ == "__main__":
    main()
