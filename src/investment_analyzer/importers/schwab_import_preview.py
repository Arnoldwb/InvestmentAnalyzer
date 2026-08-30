from dataclasses import dataclass, field
from datetime import date

from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.models.transaction import Transaction


@dataclass
class SchwabImportPreview:
    """
    Validation and summary of a proposed Schwab transaction import.

    This class does not modify or save the portfolio.
    """

    transactions: list[Transaction] = field(default_factory=list)

    transaction_count: int = 0
    buy_count: int = 0
    sell_count: int = 0

    first_date: date | None = None
    last_date: date | None = None

    net_shares: dict[str, float] = field(default_factory=dict)

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """Return True when the proposed import has no errors."""

        return not self.errors

    @property
    def status(self) -> str:
        """Return the preview status."""

        if self.errors:
            return "ERROR"

        if self.warnings:
            return "WARNING"

        return "VALID"


def analyze_transactions(
    transactions: list[Transaction],
    portfolio: Portfolio,
) -> SchwabImportPreview:
    """
    Analyze a proposed batch of imported transactions.

    The portfolio is never modified by this function.
    """

    preview = SchwabImportPreview(
        transactions=list(transactions),
    )

    preview.transaction_count = len(transactions)

    if not transactions:
        preview.errors.append(
            "The Schwab import contains no BUY or SELL transactions."
        )
        return preview

    portfolio_symbols = {
        holding.fund.symbol.upper()
        for holding in portfolio.holdings
    }

    simulated_shares = {
        holding.fund.symbol.upper(): float(holding.shares)
        for holding in portfolio.holdings
    }

    dates = []

    for row_number, transaction in enumerate(transactions, start=1):
        symbol = transaction.symbol.strip().upper()
        action = transaction.action.strip().upper()

        if action == "BUY":
            preview.buy_count += 1

        elif action == "SELL":
            preview.sell_count += 1

        else:
            preview.errors.append(
                f"Transaction {row_number}: invalid action "
                f"'{transaction.action}'."
            )
            continue

        if symbol not in portfolio_symbols:
            preview.errors.append(
                f"Transaction {row_number}: {symbol} is not "
                "in the selected portfolio."
            )
            continue

        if transaction.shares <= 0:
            preview.errors.append(
                f"Transaction {row_number}: {symbol} has "
                "non-positive share quantity."
            )
            continue

        if transaction.price < 0:
            preview.errors.append(
                f"Transaction {row_number}: {symbol} has "
                "a negative transaction price."
            )
            continue

        dates.append(transaction.date)

        if action == "BUY":
            simulated_shares[symbol] += transaction.shares

        else:
            available = simulated_shares[symbol]

            if transaction.shares > available:
                preview.errors.append(
                    f"Transaction {row_number}: cannot sell "
                    f"{transaction.shares:.3f} shares of {symbol}; "
                    f"only {available:.3f} shares would be available "
                    "at that point in the import."
                )
            else:
                simulated_shares[symbol] -= transaction.shares

        if action == "BUY":
            preview.net_shares[symbol] = (
                preview.net_shares.get(symbol, 0.0)
                + transaction.shares
            )
        elif action == "SELL":
            preview.net_shares[symbol] = (
                preview.net_shares.get(symbol, 0.0)
                - transaction.shares
            )

    if dates:
        preview.first_date = min(dates)
        preview.last_date = max(dates)

    preview.net_shares = {
        symbol: shares
        for symbol, shares in sorted(preview.net_shares.items())
    }

    if preview.errors:
        return preview

    if preview.sell_count:
        preview.warnings.append(
            f"{preview.sell_count:,} SELL transaction(s) "
            "will reduce existing holdings."
        )

    return preview
