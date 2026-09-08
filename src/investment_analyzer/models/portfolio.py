from dataclasses import dataclass, field

from .fund import Fund

from .holding import Holding
from .transaction import Transaction
from .historical_starting_position import HistoricalStartingPosition
from .historical_starting_cash import HistoricalStartingCash
from .historical_event import HistoricalEvent
from investment_analyzer.core.historical_share_history import (
    reconstruct_share_history,
)
from investment_analyzer.core.historical_cash_history import (
    reconstruct_cash_history,
)
from investment_analyzer.core.historical_value_history import (
    calculate_historical_value_history,
)
from investment_analyzer.core.historical_portfolio_value import (
    calculate_historical_portfolio_value,
)


@dataclass
class Portfolio:
    name: str = "Portfolio"

    holdings: list[Holding] = field(default_factory=list)

    transactions: list[Transaction] = field(default_factory=list)

    historical_starting_positions: list[HistoricalStartingPosition] = field(
        default_factory=list
    )

    historical_starting_cash: HistoricalStartingCash | None = None

    historical_events: list[HistoricalEvent] = field(default_factory=list)

    def add_fund(
        self,
        symbol: str,
        allocation: float,
        shares: float = 0.0,
    ) -> None:
        """Add a fund to the portfolio."""

        symbol = symbol.upper()

        if allocation <= 0:
            raise ValueError("Allocation must be greater than zero.")

        if any(holding.fund.symbol == symbol for holding in self.holdings):
            raise ValueError(f"{symbol} is already in the portfolio.")

        fund = Fund(symbol)

        self.holdings.append(
            Holding(
                fund=fund,
                allocation=allocation,
                shares=shares,
                opening_shares=shares,
            )
        )

    @staticmethod
    def _transaction_share_effect(transaction: Transaction) -> float:
        """
        Return the change in shares caused by a transaction.

        Positive values add shares.
        Negative values remove shares.
        Zero means the transaction does not affect shares.
        """

        action = transaction.action.upper()

        if action in {
            "BUY",
            "REINVEST DIVIDEND",
            "REINVEST CAPITAL GAIN",
            "ADD SHARES",
        }:
            return transaction.shares

        if action in {
            "SELL",
            "REMOVE SHARES",
        }:
            return -transaction.shares

        if action in {
            "DIVIDEND",
            "CAPITAL GAIN",
            "MANAGEMENT FEE",
            "DEPOSIT",
            "WITHDRAWAL",
            "CASH INTEREST",
            "CASH ADJUSTMENT",
        }:
            return 0.0

        raise ValueError(f"Unsupported transaction action: {action}")

    def add_transaction(
        self,
        transaction: Transaction,
    ) -> None:
        """
        Add a transaction to the portfolio.

        Share-affecting transactions update the current holding.
        Cash-only transactions do not change shares.
        """

        action = transaction.action.upper()

        cash_actions = {
            "DIVIDEND",
            "CAPITAL GAIN",
            "MANAGEMENT FEE",
            "DEPOSIT",
            "WITHDRAWAL",
            "CASH INTEREST",
            "CASH ADJUSTMENT",
        }

        if action in cash_actions:
            if transaction.shares != 0:
                raise ValueError(f"{action} must have zero shares.")

            if transaction.price != 0:
                raise ValueError(f"{action} must have zero price.")

            if transaction.amount <= 0:
                raise ValueError(f"{action} must have a positive amount.")

            transaction.symbol = ""
            transaction.action = action
            self.transactions.append(transaction)
            return

        symbol = transaction.symbol.strip().upper()

        if transaction.shares < 0:
            raise ValueError("Transaction shares cannot be negative.")

        if transaction.price < 0:
            raise ValueError("Transaction price cannot be negative.")

        holding = next(
            (holding for holding in self.holdings if holding.fund.symbol == symbol),
            None,
        )

        if holding is None:
            raise ValueError(f"{symbol} is not in the portfolio.")

        transaction.symbol = symbol
        transaction.action = action

        share_effect = self._transaction_share_effect(transaction)

        if share_effect < 0 and -share_effect > holding.shares:
            raise ValueError(
                f"Cannot remove {-share_effect:.2f} shares "
                f"of {symbol}; only {holding.shares:.2f} shares "
                "are currently held."
            )

        holding.shares += share_effect

        self.transactions.append(transaction)

    def transaction_share_balance(self, symbol: str) -> float:
        """
        Return the net share change recorded by transactions
        for a fund.
        """

        symbol = symbol.strip().upper()

        balance = 0.0

        for transaction in self.transactions:
            if transaction.symbol.upper() != symbol:
                continue

            balance += self._transaction_share_effect(transaction)

        return balance

    def opening_shares(self, symbol: str) -> float:
        """
        Return the number of shares held before recorded transactions
        began for a fund.
        """

        symbol = symbol.strip().upper()

        holding = next(
            (holding for holding in self.holdings if holding.fund.symbol == symbol),
            None,
        )

        if holding is None:
            raise ValueError(f"{symbol} is not in the portfolio.")

        return holding.starting_shares

    def recalculate_shares(self) -> None:
        """
        Recalculate current shares for all holdings from
        opening shares and recorded transactions.
        """

        for holding in self.holdings:
            shares = holding.starting_shares

            for transaction in self.transactions:
                if transaction.symbol.upper() != holding.symbol:
                    continue

                shares += self._transaction_share_effect(transaction)

            if shares < 0:
                raise ValueError(
                    f"Transactions would result in negative shares "
                    f"for {holding.symbol}."
                )

            holding.shares = shares

    def edit_transaction(
        self,
        index: int,
        transaction: Transaction,
    ) -> None:
        """
        Replace an existing transaction and recalculate share balances.
        """

        if index < 0 or index >= len(self.transactions):
            raise IndexError("Transaction index is out of range.")

        symbol = transaction.symbol.strip().upper()

        if not symbol:
            raise ValueError("Transaction symbol cannot be empty.")

        action = transaction.action.upper()

        if action not in {"BUY", "SELL"}:
            raise ValueError("Transaction action must be BUY or SELL.")

        if transaction.shares <= 0:
            raise ValueError("Transaction shares must be greater than zero.")

        if transaction.price < 0:
            raise ValueError("Transaction price cannot be negative.")

        if not any(holding.fund.symbol == symbol for holding in self.holdings):
            raise ValueError(f"{symbol} is not in the portfolio.")

        original_transaction = self.transactions[index]

        self.transactions[index] = transaction

        try:
            self.recalculate_shares()
        except Exception:
            self.transactions[index] = original_transaction
            self.recalculate_shares()
            raise

    def delete_transaction(self, index: int) -> None:
        """
        Delete an existing transaction and recalculate share balances.
        """

        if index < 0 or index >= len(self.transactions):
            raise IndexError("Transaction index is out of range.")

        transaction = self.transactions.pop(index)

        try:
            self.recalculate_shares()
        except Exception:
            self.transactions.insert(index, transaction)
            self.recalculate_shares()
            raise

    def update_allocation(self, symbol: str, allocation: float) -> None:
        """Change the allocation of an existing fund."""

        symbol = symbol.upper()

        if allocation <= 0:
            raise ValueError("Allocation must be greater than zero.")

        for holding in self.holdings:
            if holding.fund.symbol == symbol:
                holding.allocation = allocation
                return

        raise ValueError(f"{symbol} is not in the portfolio.")

    def remove_fund(self, symbol: str) -> None:
        """Remove an existing fund from the portfolio."""

        symbol = symbol.upper()

        for index, holding in enumerate(self.holdings):
            if holding.fund.symbol == symbol:
                del self.holdings[index]
                return

        raise ValueError(f"{symbol} is not in the portfolio.")

    @property
    def number_of_holdings(self) -> int:

        return len(self.holdings)

    @property
    def total_allocation(self) -> float:

        return sum(h.allocation for h in self.holdings)

    def validate(self) -> bool:

        total = self.total_allocation

        if abs(total - 100.0) > 0.01:

            raise ValueError(f"Portfolio allocations total {total:.2f}%, not 100%.")

        return True

    def transaction_historical_events(self) -> list[HistoricalEvent]:
        """
        Convert the portfolio's recorded transactions into
        historical events.

        Cash-only transactions are excluded because they do not
        change share balances.
        """

        cash_only_actions = {
            "DIVIDEND",
            "CAPITAL GAIN",
            "MANAGEMENT FEE",
            "DEPOSIT",
            "WITHDRAWAL",
            "CASH INTEREST",
            "CASH ADJUSTMENT",
        }

        events = []

        for transaction in self.transactions:
            if transaction.action.upper() in cash_only_actions:
                continue

            events.append(transaction.to_historical_event())

        return events

    def historical_cash_history(self):
        """Return the reconstructed historical cash balance."""

        if self.historical_starting_cash is None:
            raise ValueError("Historical starting cash has not been established.")

        return reconstruct_cash_history(
            self.historical_starting_cash,
            self.transactions,
        )

    def historical_value_history(self):
        """Return the reconstructed daily historical holding values."""

        share_history = reconstruct_share_history(
            self.historical_starting_positions,
            self.historical_events,
        )

        return calculate_historical_value_history(share_history)

    def historical_portfolio_value(self):
        """Return the historical total portfolio value."""

        value_history = self.historical_value_history()

        if self.historical_starting_cash is None:
            return calculate_historical_portfolio_value(value_history)

        cash_history = self.historical_cash_history()

        return calculate_historical_portfolio_value(
            value_history,
            cash_history,
        )

    def summary(self) -> None:

        print()

        print(self.name)

        print("-" * 40)

        for holding in self.holdings:

            print(f"{holding.fund.symbol:8}{holding.allocation:6.1f}%")

        print("-" * 40)

        print(f"Total{'':3}{self.total_allocation:6.1f}%")
