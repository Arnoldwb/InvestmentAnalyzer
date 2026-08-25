import re
from datetime import date
from pathlib import Path

import pandas as pd

from investment_analyzer.core.fund_metadata import load_fund_metadata
from investment_analyzer.models.transaction import Transaction


class SchwabTransactionImporter:
    """
    Import BUY and SELL transactions from a Schwab CSV export.
    """

    REQUIRED_COLUMNS = {
        "Date",
        "Type",
        "Security/Payee",
        "Description/Category",
        "Invest Amt",
        "Amount",
    }

    def __init__(self):
        self.metadata = load_fund_metadata()
        self.name_to_symbol = self._build_name_lookup()

    def _normalize_name(self, name: str) -> str:
        """
        Normalize a fund name for comparison.
        """

        name = str(name).upper().strip()

        name = re.sub(r"\(R\)", "", name)

        name = name.replace("ACTIVEBETAEMERGING", "ACTIVEBETA EMERGING")
        name = name.replace("ACTIVEBETAINTERNATIONAL", "ACTIVEBETA INTERNATIONAL")
        name = name.replace("ACTIVEBETAU.S.", "ACTIVEBETA U.S.")
        name = name.replace("MARKETSEQUITY", "MARKETS EQUITY")
        name = name.replace("BONDINDEX", "BOND INDEX")

        replacements = {
            "U.S.": "US",
            "U.S": "US",
            "EQTY": "EQUITY",
            "INTL": "INTERNATIONAL",
            "INCM": "INCOME",
            "FD": "FUND",
            "INST": "INSTITUTIONAL",
            "CL": "CLASS",
            "SHRS": "",
            "SHR": "",
        }

        for old, new in replacements.items():
            name = re.sub(
                rf"\b{re.escape(old)}\b",
                new,
                name,
            )

        name = re.sub(r"[^A-Z0-9]+", " ", name)

        name = re.sub(r"\s+", " ", name).strip()

        return name

    def _build_name_lookup(self) -> dict[str, str]:
        """
        Build a normalized fund-name → symbol lookup
        from fund_metadata.json.
        """

        lookup = {}

        for symbol, entry in self.metadata.items():
            if not isinstance(entry, dict):
                continue

            name = entry.get("name")

            if not isinstance(name, str):
                continue

            normalized = self._normalize_name(name)

            if normalized:
                lookup[normalized] = symbol.upper()

        return lookup

    def _find_symbol(self, fund_name: str) -> str:
        """
        Match a Schwab fund name to an Investment Analyzer symbol.
        """

        normalized = self._normalize_name(fund_name)

        symbol = self.name_to_symbol.get(normalized)

        if symbol is None:
            raise ValueError(
                f"Unable to match Schwab fund name to "
                f"Investment Analyzer fund: {fund_name}"
            )

        return symbol

    def _parse_description(self, description: str) -> tuple[float, float]:
        """
        Extract shares and price from:

            669.823 shares @ 3.00
        """

        pattern = (
            r"^\s*"
            r"([\d,]+(?:\.\d+)?)"
            r"\s+shares\s+@\s+"
            r"([\d,]+(?:\.\d+)?)"
            r"\s*$"
        )

        match = re.match(pattern, str(description), re.IGNORECASE)

        if not match:
            raise ValueError(
                f"Unable to parse transaction description: " f"{description}"
            )

        shares = float(match.group(1).replace(",", ""))
        price = float(match.group(2).replace(",", ""))

        if shares <= 0:
            raise ValueError("Transaction shares must be greater than zero.")

        if price < 0:
            raise ValueError("Transaction price cannot be negative.")

        return shares, price

    def import_file(
        self,
        csv_path: str | Path,
    ) -> list[Transaction]:
        """
        Import BUY and SELL transactions from a Schwab CSV file.
        """

        path = Path(csv_path)

        if not path.exists():
            raise FileNotFoundError(f"Schwab CSV file not found: {path}")

        dataframe = pd.read_csv(path)

        missing = self.REQUIRED_COLUMNS - set(dataframe.columns)

        if missing:
            raise ValueError(
                "Schwab CSV is missing required columns: " + ", ".join(sorted(missing))
            )

        transactions: list[Transaction] = []

        for row_number, row in dataframe.iterrows():
            action = str(row["Type"]).strip().upper()

            if action not in {"BUY", "SELL"}:
                continue

            transaction_date = pd.to_datetime(row["Date"]).date()

            fund_name = str(row["Security/Payee"]).strip()

            shares, price = self._parse_description(row["Description/Category"])

            symbol = self._find_symbol(fund_name)

            transactions.append(
                Transaction(
                    date=transaction_date,
                    symbol=symbol,
                    action=action,
                    shares=shares,
                    price=price,
                    note=f"Imported from Schwab: {fund_name}",
                )
            )

        transactions.sort(key=lambda transaction: transaction.date)

        return transactions
