"""
Vanguard transaction importer for Investment Analyzer.

Converts Vanguard Quicken CSV activity into Investment Analyzer
Transaction objects.
"""

import re
from pathlib import Path

import pandas as pd

from investment_analyzer.models.transaction import (
    Transaction,
    TransactionAction,
)


class VanguardTransactionImporter:
    """Import Vanguard historical activity as Transaction objects."""

    CASH_TYPES = {
        "Dividend Income",
        "Long-term Capital Gain",
        "Short-term Capital Gain",
        "Payment/Deposit",
    }

    SHARE_TYPES = {
        "Buy",
        "Sell",
        "Reinvest Dividend",
        "Add Shares",
        "Remove Shares",
    }

    SECURITY_NAME_MAP = {
        "Vanguard Wellington Fund Admiral Shares": "Vanguard Wellington Admiral",
    }

    @classmethod
    def import_file(
        cls,
        csv_file: str | Path,
    ) -> list[Transaction]:
        """Import Vanguard activity and return transactions sorted by date."""

        path = Path(csv_file)

        if not path.exists():
            raise FileNotFoundError(f"Vanguard CSV file not found: {path}")

        data = pd.read_csv(path)

        transactions = []

        for row_number, row in data.iterrows():
            if pd.isna(row.get("Date")) or pd.isna(row.get("Type")):
                continue

            transaction_type = str(row["Type"]).strip()

            if transaction_type in cls.SHARE_TYPES:
                transaction = cls._parse_share_transaction(
                    row,
                    row_number + 2,
                )

            elif transaction_type in cls.CASH_TYPES:
                transaction = cls._parse_cash_transaction(
                    row,
                    row_number + 2,
                )

            else:
                continue

            if transaction is not None:
                transactions.append(transaction)

        transactions.sort(key=lambda transaction: transaction.date)

        return transactions

    @classmethod
    def _parse_share_transaction(
        cls,
        row,
        line_number: int,
    ) -> Transaction | None:
        """Convert one Vanguard share transaction."""

        transaction_type = str(row["Type"]).strip()
        security = str(row.get("Security/Payee", "")).strip()

        if not security or security == "nan":
            return None

        security = cls.SECURITY_NAME_MAP.get(
            security,
            security,
        )

        description = str(row.get("Description/Category", "")).strip()

        shares_match = re.search(
            r"([+-]?\d[\d,]*\.?\d*)\s+shares",
            description,
            re.IGNORECASE,
        )

        if not shares_match:
            return None

        shares = abs(float(shares_match.group(1).replace(",", "")))

        price_match = re.search(
            r"@\s*\$?([\d,]+(?:\.\d+)?)",
            description,
            re.IGNORECASE,
        )

        price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

        amount = pd.to_numeric(
            str(row.get("Amount", "")).replace(",", ""),
            errors="coerce",
        )

        amount = float(amount) if pd.notna(amount) else 0.0

        action = {
            "Buy": TransactionAction.BUY,
            "Sell": TransactionAction.SELL,
            "Reinvest Dividend": TransactionAction.REINVEST_DIVIDEND,
            "Add Shares": TransactionAction.ADD_SHARES,
            "Remove Shares": TransactionAction.REMOVE_SHARES,
        }[transaction_type]

        return Transaction(
            date=pd.to_datetime(row["Date"]).date(),
            symbol=security,
            action=action,
            shares=shares,
            price=price,
            note=f"Imported from Vanguard: {transaction_type}",
            amount=abs(amount),
        )

    @classmethod
    def _parse_cash_transaction(
        cls,
        row,
        line_number: int,
    ) -> Transaction | None:
        """Convert one Vanguard cash transaction."""

        transaction_type = str(row["Type"]).strip()

        amount = pd.to_numeric(
            str(row.get("Amount", "")).replace(",", ""),
            errors="coerce",
        )

        if pd.isna(amount) or float(amount) == 0.0:
            return None

        amount = float(amount)

        if transaction_type == "Dividend Income":
            action = TransactionAction.DIVIDEND

        elif transaction_type in {
            "Long-term Capital Gain",
            "Short-term Capital Gain",
        }:
            action = TransactionAction.CAPITAL_GAIN

        elif transaction_type == "Payment/Deposit":
            action = (
                TransactionAction.DEPOSIT
                if amount > 0
                else TransactionAction.WITHDRAWAL
            )
            amount = abs(amount)

        else:
            return None

        if transaction_type == "Payment/Deposit":
            security = ""
        else:
            security = str(row.get("Security/Payee", "")).strip()

            if security == "nan":
                security = ""

        return Transaction(
            date=pd.to_datetime(row["Date"]).date(),
            symbol=security,
            action=action,
            shares=0.0,
            price=0.0,
            note=f"Imported from Vanguard: {transaction_type}",
            amount=abs(amount),
        )
