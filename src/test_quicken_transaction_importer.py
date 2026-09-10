from pathlib import Path

from investment_analyzer.models.transaction import Transaction
from investment_analyzer.importers.quicken_transaction_importer import (
    QuickenTransactionImporter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_import_quicken_transactions():
    files = [
        PROJECT_ROOT
        / "transactions"
        / "historical"
        / "Export-SCHWAB_AWB-ROTH_2026-09-03.csv",
        PROJECT_ROOT
        / "transactions"
        / "historical"
        / "Export-SCHWAB_EB-ROTH_2006-09-03.csv",
        PROJECT_ROOT
        / "transactions"
        / "historical"
        / "Export-SCHWAB_FAMILY_TRUST_2026-09-03.csv",
        PROJECT_ROOT
        / "transactions"
        / "historical"
        / "Export-SCHWAB_LIVING_TRUST_2026-09-03.csv",
        PROJECT_ROOT
        / "transactions"
        / "historical"
        / "Export-VANGUARD_2026-09-04csv.csv",
    ]

    importer = QuickenTransactionImporter()

    all_transactions = []

    for path in files:
        transactions = importer.import_file(path)

        assert all(isinstance(transaction, Transaction) for transaction in transactions)

        all_transactions.extend(transactions)

    assert all_transactions

    actions = {transaction.action for transaction in all_transactions}

    assert "BUY" in actions
    assert "SELL" in actions
    assert "DIVIDEND" in actions
    assert "CAPITAL_GAIN" in actions
    assert "REINVEST_DIVIDEND" in actions
    assert "REINVEST_CAPITAL_GAIN" in actions
    assert "ADD_SHARES" in actions
    assert "REMOVE_SHARES" in actions
    assert "DEPOSIT" in actions
    assert "WITHDRAWAL" in actions
    assert "MANAGEMENT_FEE" in actions
    assert "CASH_INTEREST" in actions
    assert "CASH_ADJUSTMENT" in actions
    # Verify all Vanguard capital-gain distributions, including
    # comma-formatted amounts.
    capital_gains = [
        transaction
        for transaction in all_transactions
        if transaction.action == "CAPITAL_GAIN"
    ]

    assert len(capital_gains) == 6

    assert any(
        transaction.symbol == "VGHAX"
        and transaction.amount == 9262.69
        and transaction.date.isoformat() == "2024-12-23"
        for transaction in capital_gains
    )

    assert any(
        transaction.symbol == "VGHAX"
        and transaction.amount == 498.06
        and transaction.date.isoformat() == "2024-12-23"
        for transaction in capital_gains
    )

    assert any(
        transaction.symbol == "VWENX"
        and transaction.amount == 491.78
        and transaction.date.isoformat() == "2024-12-31"
        for transaction in capital_gains
    )

    assert any(
        transaction.symbol == "VWENX"
        and transaction.amount == 8201.58
        and transaction.date.isoformat() == "2024-12-31"
        for transaction in capital_gains
    )

    assert any(
        transaction.symbol == "VWENX"
        and transaction.amount == 8160.63
        and transaction.date.isoformat() == "2025-12-24"
        for transaction in capital_gains
    )

    assert any(
        transaction.symbol == "VWENX"
        and transaction.amount == 1717.30
        and transaction.date.isoformat() == "2025-12-24"
        for transaction in capital_gains
    )
    # Verify representative cash transactions.
    deposits = [
        transaction
        for transaction in all_transactions
        if transaction.action == "DEPOSIT"
    ]

    assert len(deposits) == 6
    assert any(
        transaction.amount == 77.78 and transaction.date.isoformat() == "2023-09-05"
        for transaction in deposits
    )
    assert any(
        transaction.amount == 28.59 and transaction.date.isoformat() == "2025-12-22"
        for transaction in deposits
    )
    assert any(
        transaction.amount == 3783.02 and transaction.date.isoformat() == "2022-05-04"
        for transaction in deposits
    )

    assert any(
        transaction.amount == 250000.00 and transaction.date.isoformat() == "2025-12-16"
        for transaction in deposits
    )

    withdrawals = [
        transaction
        for transaction in all_transactions
        if transaction.action == "WITHDRAWAL"
    ]

    assert len(withdrawals) == 15

    assert any(
        transaction.amount == 616.00 and transaction.date.isoformat() == "2026-06-22"
        for transaction in withdrawals
    )

    assert any(
        transaction.amount == 5000.00 and transaction.date.isoformat() == "2024-09-27"
        for transaction in withdrawals
    )

    assert any(
        transaction.amount == 9262.69 and transaction.date.isoformat() == "2024-12-23"
        for transaction in withdrawals
    )

    assert any(
        transaction.amount == 8811.60 and transaction.date.isoformat() == "2025-01-13"
        for transaction in withdrawals
    )

    assert any(
        transaction.amount == 45000.00 and transaction.date.isoformat() == "2026-07-17"
        for transaction in withdrawals
    )

    cash_adjustments = [
        transaction
        for transaction in all_transactions
        if transaction.action == "CASH_ADJUSTMENT"
    ]

    assert len(cash_adjustments) == 8
    assert any(
        transaction.amount == 21209.47 and transaction.date.isoformat() == "2023-04-18"
        for transaction in cash_adjustments
    )
    cash_interest = [
        transaction
        for transaction in all_transactions
        if transaction.action == "CASH_INTEREST"
    ]

    assert len(cash_interest) == 148

    management_fees = [
        transaction
        for transaction in all_transactions
        if transaction.action == "MANAGEMENT_FEE"
    ]

    assert len(management_fees) == 192
