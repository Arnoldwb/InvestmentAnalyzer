"""
Generic Investment Analyzer transaction CSV importer.

Expected CSV columns:

Date,Symbol,Action,Shares,Price,Amount,Note
"""

import csv
from datetime import datetime
from pathlib import Path

from investment_analyzer.models.transaction import Transaction, TransactionAction


class TransactionCSVImporter:
    """Import standardized Investment Analyzer transaction CSV files."""

    REQUIRED_COLUMNS = {
        "Date",
        "Symbol",
        "Action",
    }

    SHARE_ACTIONS = {
        TransactionAction.BUY,
        TransactionAction.SELL,
        TransactionAction.REINVEST_DIVIDEND,
        TransactionAction.REINVEST_CAPITAL_GAIN,
        TransactionAction.ADD_SHARES,
        TransactionAction.REMOVE_SHARES,
    }

    CASH_ACTIONS = {
        TransactionAction.DIVIDEND,
        TransactionAction.CAPITAL_GAIN,
        TransactionAction.MANAGEMENT_FEE,
    }

    @classmethod
    def import_file(cls, file_path: str | Path) -> list[Transaction]:
        """
        Import transactions from a standardized CSV file.

        Returns transactions sorted by date.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Transaction CSV not found: {path}")

        with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise ValueError("Transaction CSV is missing a header row.")

            missing_columns = cls.REQUIRED_COLUMNS - set(reader.fieldnames)

            if missing_columns:
                missing = ", ".join(sorted(missing_columns))
                raise ValueError(
                    f"Transaction CSV is missing required columns: {missing}"
                )

            transactions = []

            for line_number, row in enumerate(reader, start=2):
                transactions.append(
                    cls._parse_row(row, line_number)
                )

        transactions.sort(key=lambda transaction: transaction.date)

        return transactions

    @classmethod
    def _parse_row(
        cls,
        row: dict[str, str],
        line_number: int,
    ) -> Transaction:
        """Convert one CSV row into a Transaction."""

        try:
            transaction_date = datetime.strptime(
                row["Date"].strip(),
                "%Y-%m-%d",
            ).date()
        except (ValueError, AttributeError) as exc:
            raise ValueError(
                f"Invalid transaction date on CSV line {line_number}: "
                f"{row.get('Date', '')!r}"
            ) from exc

        symbol = row["Symbol"].strip().upper()

        if not symbol:
            raise ValueError(
                f"Transaction symbol cannot be empty on CSV line {line_number}."
            )

        action = row["Action"].strip().upper()

        valid_actions = cls.SHARE_ACTIONS | cls.CASH_ACTIONS

        if action not in valid_actions:
            raise ValueError(
                f"Unsupported transaction action on CSV line {line_number}: "
                f"{action!r}"
            )

        shares = cls._parse_number(
            row.get("Shares", ""),
            "shares",
            line_number,
        )

        price = cls._parse_number(
            row.get("Price", ""),
            "price",
            line_number,
        )

        amount_text = row.get("Amount", "").strip()

        if amount_text:
            amount = cls._parse_number(
                amount_text,
                "amount",
                line_number,
            )
        else:
            amount = 0.0

        note = row.get("Note", "").strip()

        if shares < 0:
            raise ValueError(
                f"Transaction shares cannot be negative on CSV line "
                f"{line_number}."
            )

        if price < 0:
            raise ValueError(
                f"Transaction price cannot be negative on CSV line "
                f"{line_number}."
            )

        if amount < 0:
            raise ValueError(
                f"Transaction amount cannot be negative on CSV line "
                f"{line_number}."
            )

        if action in cls.CASH_ACTIONS:
            if shares != 0.0:
                raise ValueError(
                    f"{action} must have zero shares on CSV line "
                    f"{line_number}."
                )

            if price != 0.0:
                raise ValueError(
                    f"{action} must have zero price on CSV line "
                    f"{line_number}."
                )

            if amount <= 0:
                raise ValueError(
                    f"{action} must have a positive amount on CSV line "
                    f"{line_number}."
                )

        else:
            if shares <= 0:
                raise ValueError(
                    f"{action} must have positive shares on CSV line "
                    f"{line_number}."
                )

            if price < 0:
                raise ValueError(
                    f"{action} cannot have a negative price on CSV line "
                    f"{line_number}."
                )

            if amount == 0.0:
                amount = shares * price

        return Transaction(
            date=transaction_date,
            symbol=symbol,
            action=action,
            shares=shares,
            price=price,
            note=note,
            amount=amount,
        )

    @staticmethod
    def _parse_number(
        value: str | None,
        field_name: str,
        line_number: int,
    ) -> float:
        """Parse a numeric CSV field."""

        text = (value or "").strip()

        if not text:
            return 0.0

        try:
            return float(text.replace(",", ""))
        except ValueError as exc:
            raise ValueError(
                f"Invalid {field_name} on CSV line {line_number}: {value!r}"
            ) from exc
