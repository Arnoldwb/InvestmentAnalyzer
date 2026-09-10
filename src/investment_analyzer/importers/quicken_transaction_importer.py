import re
from datetime import date
from pathlib import Path

import pandas as pd

from investment_analyzer.core.fund_metadata import load_fund_metadata
from investment_analyzer.core.paths import TRANSACTION_DIR
from investment_analyzer.models.transaction import Transaction


class QuickenTransactionImporter:
    """
    Import Quicken historical investment activity into Transactions.
    """

    REQUIRED_COLUMNS = {
        "Date",
        "Type",
        "Security/Payee",
        "Description/Category",
        "Shares In",
        "Shares Out",
        "Cash In",
        "Cash Out",
        "Invest Amt",
    }

    def __init__(self):
        self.metadata = load_fund_metadata()
        self.name_to_symbol = self._build_name_lookup()

    def _normalize_name(self, name: str) -> str:
        """
        Normalize a security name for comparison.
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
                flags=re.IGNORECASE,
            )

        name = re.sub(r"[^A-Z0-9]+", " ", name)
        name = re.sub(r"\s+", " ", name).strip()

        return name

    def _build_name_lookup(self) -> dict[str, str]:
        """
        Build normalized fund-name → symbol lookup.
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
        # Known Quicken security-name aliases.
        lookup[self._normalize_name("ISHRS CORE MOD ALLO")] = "AOM"
        lookup[self._normalize_name("Vanguard Health Care-Admiral")] = "VGHAX"
        lookup[self._normalize_name("Vanguard Wellington Admiral")] = "VWENX"
        lookup[self._normalize_name("Vanguard Federal Money Market Fund")] = "VMFXX"

        return lookup

    def _find_symbol(self, security_name: str) -> str:
        """
        Match a Quicken security name to an Investment Analyzer symbol.
        """

        normalized = self._normalize_name(security_name)

        symbol = self.name_to_symbol.get(normalized)

        if symbol is None:
            raise ValueError(
                f"Unable to match Quicken security name to "
                f"Investment Analyzer fund: {security_name}"
            )

        return symbol

    @staticmethod
    def _parse_amount(value) -> float:
        """
        Parse a Quicken dollar amount, including comma-formatted values.

        Examples:
            498.06   -> 498.06
            "9,262.69" -> 9262.69
            None / NaN -> 0.0
        """
        if value is None:
            return 0.0

        text = str(value).strip().replace(",", "")

        if not text or text.lower() == "nan":
            return 0.0

        try:
            return float(text)
        except ValueError:
            return 0.0

    @staticmethod
    def _parse_description(description: str) -> tuple[float, float]:
        """
        Extract shares and optional price from a Quicken description.

        Examples:
            669.823 shares @ 3.00
            460 shares
        """

        pattern = (
            r"^\s*"
            r"([\d,]+(?:\.\d+)?)"
            r"\s+shares?"
            r"(?:\s+@\s+([\d,]+(?:\.\d+)?))?"
            r"\s*$"
        )

        match = re.match(pattern, str(description), re.IGNORECASE)

        if not match:
            raise ValueError(f"Unable to parse transaction description: {description}")

        shares = float(match.group(1).replace(",", ""))

        price_text = match.group(2)
        price = float(price_text.replace(",", "")) if price_text is not None else 0.0

        if shares <= 0:
            raise ValueError("Transaction shares must be greater than zero.")

        return shares, price

    def import_file(
        self,
        csv_path: str | Path,
    ) -> list[Transaction]:
        """
        Import Buy, Sell, and Dividend Income transactions
        from a Quicken CSV file.
        """

        path = Path(csv_path)

        if not path.is_absolute():
            path = TRANSACTION_DIR / path

        if not path.exists():
            raise FileNotFoundError(f"Quicken CSV file not found: {path}")

        dataframe = pd.read_csv(path)

        missing = self.REQUIRED_COLUMNS - set(dataframe.columns)

        if missing:
            raise ValueError(
                "Quicken CSV is missing required columns: " + ", ".join(sorted(missing))
            )

        transactions: list[Transaction] = []

        for _, row in dataframe.iterrows():
            action = str(row["Type"]).strip()

            if action not in {
                "Buy",
                "Sell",
                "Dividend Income",
                "Long-term Capital Gain",
                "Short-term Capital Gain",
                "Reinvest Dividend",
                "Reinvest Long-term Capital Gain",
                "Reinvest Short-term Capital Gain",
                "Add Shares",
                "Remove Shares",
                "Payment/Deposit",
                "Miscellaneous Expense",
            }:
                continue

            transaction_date = pd.to_datetime(row["Date"]).date()
            security_name = str(row["Security/Payee"]).strip()

            if not security_name or security_name == "nan":
                security_name = ""

            cash_actions = {
                "Payment/Deposit",
                "Miscellaneous Expense",
            }

            if action in cash_actions:
                symbol = ""
            elif not security_name:
                continue
            else:
                symbol = self._find_symbol(security_name)

            if action in {
                "Buy",
                "Sell",
                "Reinvest Dividend",
                "Reinvest Long-term Capital Gain",
                "Reinvest Short-term Capital Gain",
                "Add Shares",
                "Remove Shares",
            }:
                shares, price = self._parse_description(row["Description/Category"])

                amount = self._parse_amount(row["Invest Amt"])
                amount = float(amount) if pd.notna(amount) else 0.0

                transactions.append(
                    Transaction(
                        date=transaction_date,
                        symbol=symbol,
                        action=(
                            "REINVEST_DIVIDEND"
                            if action == "Reinvest Dividend"
                            else (
                                "REINVEST_CAPITAL_GAIN"
                                if action
                                in {
                                    "Reinvest Long-term Capital Gain",
                                    "Reinvest Short-term Capital Gain",
                                }
                                else (
                                    "ADD_SHARES"
                                    if action == "Add Shares"
                                    else (
                                        "REMOVE_SHARES"
                                        if action == "Remove Shares"
                                        else action.upper()
                                    )
                                )
                            )
                        ),
                        shares=shares,
                        price=price,
                        amount=abs(amount),
                        note=f"Imported from Quicken: {security_name}",
                    )
                )
            elif action == "Payment/Deposit":
                description = str(row["Description/Category"]).strip()
                security = str(row["Security/Payee"]).strip()

                description_lower = description.lower()
                security_lower = security.lower()

                cash_in = self._parse_amount(row["Cash In"])
                cash_out = self._parse_amount(row["Cash Out"])

                if (
                    "mgmtfee to advisor" in security_lower
                    or "mgmtfee to advisor" in description_lower
                    or "abp fee" in security_lower
                ):
                    if pd.notna(cash_out) and float(cash_out) > 0:
                        transactions.append(
                            Transaction(
                                date=transaction_date,
                                symbol="",
                                action="MANAGEMENT_FEE",
                                shares=0,
                                price=0,
                                amount=float(cash_out),
                                note=f"Imported from Quicken: {security}",
                            )
                        )
                elif (
                    "reconcile adjustment" in security_lower
                    or "reconcile adjustment" in description_lower
                ):
                    amount = cash_in if pd.notna(cash_in) and cash_in > 0 else cash_out
                    if pd.notna(amount) and float(amount) > 0:
                        transactions.append(
                            Transaction(
                                date=transaction_date,
                                symbol="",
                                action="CASH_ADJUSTMENT",
                                shares=0,
                                price=0,
                                amount=float(amount),
                                note=f"Imported from Quicken: {security}",
                            )
                        )
                elif (
                    "bank int" in security_lower
                    or "bank interest" in security_lower
                    or "bank interest" in description_lower
                ):
                    if pd.notna(cash_in) and float(cash_in) > 0:
                        transactions.append(
                            Transaction(
                                date=transaction_date,
                                symbol="",
                                action="CASH_INTEREST",
                                shares=0,
                                price=0,
                                amount=float(cash_in),
                                note=f"Imported from Quicken: {security}",
                            )
                        )
                elif pd.notna(cash_in) and float(cash_in) > 0:
                    transactions.append(
                        Transaction(
                            date=transaction_date,
                            symbol="",
                            action="DEPOSIT",
                            shares=0,
                            price=0,
                            amount=float(cash_in),
                            note=f"Imported from Quicken: {security}",
                        )
                    )
                elif pd.notna(cash_out) and float(cash_out) > 0:
                    transactions.append(
                        Transaction(
                            date=transaction_date,
                            symbol="",
                            action="WITHDRAWAL",
                            shares=0,
                            price=0,
                            amount=float(cash_out),
                            note=f"Imported from Quicken: {security}",
                        )
                    )
            elif action == "Miscellaneous Expense":
                cash_out = self._parse_amount(row["Cash Out"])

                if pd.isna(cash_out) or float(cash_out) <= 0:
                    continue

                transactions.append(
                    Transaction(
                        date=transaction_date,
                        symbol="",
                        action="MANAGEMENT_FEE",
                        shares=0,
                        price=0,
                        amount=float(cash_out),
                        note=f"Imported from Quicken: {security_name}",
                    )
                )
            elif action == "Dividend Income":
                amount = self._parse_amount(row["Cash In"])

                if pd.isna(amount):
                    continue

                transactions.append(
                    Transaction(
                        date=transaction_date,
                        symbol=symbol,
                        action="DIVIDEND",
                        shares=0.0,
                        price=0.0,
                        amount=abs(float(amount)),
                        note=f"Imported from Quicken: {security_name}",
                    )
                )
            elif action in {
                "Long-term Capital Gain",
                "Short-term Capital Gain",
            }:
                amount = self._parse_amount(row["Cash In"])

                if pd.isna(amount):
                    continue

                transactions.append(
                    Transaction(
                        date=transaction_date,
                        symbol=symbol,
                        action="CAPITAL_GAIN",
                        shares=0.0,
                        price=0.0,
                        amount=abs(float(amount)),
                        note=f"Imported from Quicken: {security_name}",
                    )
                )

        transactions.sort(key=lambda transaction: transaction.date)

        return transactions
