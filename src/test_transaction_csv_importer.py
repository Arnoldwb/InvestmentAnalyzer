"""
Regression tests for the generic transaction CSV importer.
"""

import csv

import pytest

from investment_analyzer.importers.transaction_csv_importer import (
    TransactionCSVImporter,
)
from investment_analyzer.models.transaction import TransactionAction


def write_csv(path, rows):
    fieldnames = [
        "Date",
        "Symbol",
        "Action",
        "Shares",
        "Price",
        "Amount",
        "Note",
    ]

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_import_all_supported_transaction_actions(tmp_path):
    csv_path = tmp_path / "transactions.csv"

    rows = [
        {
            "Date": "2026-09-06",
            "Symbol": "AVEM",
            "Action": "BUY",
            "Shares": "10",
            "Price": "100",
            "Amount": "",
            "Note": "Purchase",
        },
        {
            "Date": "2026-09-05",
            "Symbol": "AVEM",
            "Action": "SELL",
            "Shares": "2",
            "Price": "110",
            "Amount": "220",
            "Note": "",
        },
        {
            "Date": "2026-09-04",
            "Symbol": "AVEM",
            "Action": "DIVIDEND",
            "Shares": "0",
            "Price": "0",
            "Amount": "25.50",
            "Note": "Cash dividend",
        },
        {
            "Date": "2026-09-03",
            "Symbol": "DFNM",
            "Action": "REINVEST DIVIDEND",
            "Shares": "5",
            "Price": "10",
            "Amount": "50",
            "Note": "",
        },
        {
            "Date": "2026-09-02",
            "Symbol": "DFNM",
            "Action": "CAPITAL GAIN",
            "Shares": "0",
            "Price": "0",
            "Amount": "12.75",
            "Note": "",
        },
        {
            "Date": "2026-09-01",
            "Symbol": "DFNM",
            "Action": "REINVEST CAPITAL GAIN",
            "Shares": "1.25",
            "Price": "10",
            "Amount": "12.50",
            "Note": "",
        },
        {
            "Date": "2026-08-31",
            "Symbol": "DFNM",
            "Action": "MANAGEMENT FEE",
            "Shares": "0",
            "Price": "0",
            "Amount": "5.25",
            "Note": "Quarterly fee",
        },
        {
            "Date": "2026-08-30",
            "Symbol": "DFNM",
            "Action": "ADD SHARES",
            "Shares": "3",
            "Price": "0",
            "Amount": "",
            "Note": "Opening position",
        },
        {
            "Date": "2026-08-29",
            "Symbol": "DFNM",
            "Action": "REMOVE SHARES",
            "Shares": "1",
            "Price": "0",
            "Amount": "",
            "Note": "Administrative adjustment",
        },
        {
            "Date": "2026-08-28",
            "Symbol": "",
            "Action": "DEPOSIT",
            "Shares": "0",
            "Price": "0",
            "Amount": "1000",
            "Note": "Cash deposit",
        },
        {
            "Date": "2026-08-27",
            "Symbol": "",
            "Action": "WITHDRAWAL",
            "Shares": "0",
            "Price": "0",
            "Amount": "250",
            "Note": "Cash withdrawal",
        },
        {
            "Date": "2026-08-26",
            "Symbol": "",
            "Action": "CASH INTEREST",
            "Shares": "0",
            "Price": "0",
            "Amount": "3.75",
            "Note": "Cash interest",
        },
        {
            "Date": "2026-08-25",
            "Symbol": "",
            "Action": "CASH ADJUSTMENT",
            "Shares": "0",
            "Price": "0",
            "Amount": "7.50",
            "Note": "Cash adjustment",
        },
    ]

    write_csv(csv_path, rows)

    transactions = TransactionCSVImporter.import_file(csv_path)

    assert len(transactions) == 13

    # Importer sorts transactions chronologically.
    assert transactions[0].date.isoformat() == "2026-08-25"
    assert transactions[-1].date.isoformat() == "2026-09-06"

    actions = {transaction.action for transaction in transactions}

    assert actions == {
        TransactionAction.BUY,
        TransactionAction.SELL,
        TransactionAction.DIVIDEND,
        TransactionAction.REINVEST_DIVIDEND,
        TransactionAction.CAPITAL_GAIN,
        TransactionAction.REINVEST_CAPITAL_GAIN,
        TransactionAction.MANAGEMENT_FEE,
        TransactionAction.ADD_SHARES,
        TransactionAction.REMOVE_SHARES,
        TransactionAction.DEPOSIT,
        TransactionAction.WITHDRAWAL,
        TransactionAction.CASH_INTEREST,
        TransactionAction.CASH_ADJUSTMENT,
    }


def test_blank_amount_is_calculated_for_share_transaction(tmp_path):
    csv_path = tmp_path / "transactions.csv"

    write_csv(
        csv_path,
        [
            {
                "Date": "2026-09-06",
                "Symbol": "AVEM",
                "Action": "BUY",
                "Shares": "12.5",
                "Price": "80",
                "Amount": "",
                "Note": "",
            }
        ],
    )

    transactions = TransactionCSVImporter.import_file(csv_path)

    assert transactions[0].amount == pytest.approx(1000.0)


def test_cash_transaction_requires_amount(tmp_path):
    csv_path = tmp_path / "transactions.csv"

    write_csv(
        csv_path,
        [
            {
                "Date": "2026-09-06",
                "Symbol": "AVEM",
                "Action": "DIVIDEND",
                "Shares": "0",
                "Price": "0",
                "Amount": "",
                "Note": "",
            }
        ],
    )

    with pytest.raises(ValueError, match="positive amount"):
        TransactionCSVImporter.import_file(csv_path)


def test_invalid_action_is_rejected(tmp_path):
    csv_path = tmp_path / "transactions.csv"

    write_csv(
        csv_path,
        [
            {
                "Date": "2026-09-06",
                "Symbol": "AVEM",
                "Action": "TRANSFER",
                "Shares": "10",
                "Price": "100",
                "Amount": "",
                "Note": "",
            }
        ],
    )

    with pytest.raises(ValueError, match="Unsupported transaction action"):
        TransactionCSVImporter.import_file(csv_path)


def test_missing_required_column_is_rejected(tmp_path):
    csv_path = tmp_path / "transactions.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "Date",
                "Symbol",
            ]
        )
        writer.writerow(
            [
                "2026-09-06",
                "AVEM",
            ]
        )

    with pytest.raises(ValueError, match="missing required columns"):
        TransactionCSVImporter.import_file(csv_path)


def test_cash_transaction_rejects_shares_and_price(tmp_path):
    csv_path = tmp_path / "transactions.csv"

    write_csv(
        csv_path,
        [
            {
                "Date": "2026-09-06",
                "Symbol": "AVEM",
                "Action": "DIVIDEND",
                "Shares": "1",
                "Price": "100",
                "Amount": "25",
                "Note": "",
            }
        ],
    )

    with pytest.raises(ValueError, match="zero shares"):
        TransactionCSVImporter.import_file(csv_path)


def test_symbol_is_normalized(tmp_path):
    csv_path = tmp_path / "transactions.csv"

    write_csv(
        csv_path,
        [
            {
                "Date": "2026-09-06",
                "Symbol": " avem ",
                "Action": "buy",
                "Shares": "10",
                "Price": "100",
                "Amount": "",
                "Note": "",
            }
        ],
    )

    transactions = TransactionCSVImporter.import_file(csv_path)

    assert transactions[0].symbol == "AVEM"
    assert transactions[0].action == TransactionAction.BUY
