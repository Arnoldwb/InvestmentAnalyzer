from dataclasses import dataclass, field

from .fund import Fund

from .holding import Holding
from .transaction import Transaction


@dataclass
class Portfolio:
    name: str = "Portfolio"

    holdings: list[Holding] = field(default_factory=list)

    transactions: list[Transaction] = field(default_factory=list)

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

    def add_transaction(
        self,
        transaction: Transaction,
    ) -> None:
        """
        Add a transaction to the portfolio.

        BUY transactions increase shares.
        SELL transactions decrease shares.
        """

        symbol = transaction.symbol.strip().upper()

        if not symbol:
            raise ValueError("Transaction symbol cannot be empty.")

        if transaction.action.upper() not in {"BUY", "SELL"}:
            raise ValueError("Transaction action must be BUY or SELL.")

        if transaction.shares <= 0:
            raise ValueError("Transaction shares must be greater than zero.")

        if transaction.price < 0:
            raise ValueError("Transaction price cannot be negative.")

        holding = next(
            (holding for holding in self.holdings if holding.fund.symbol == symbol),
            None,
        )

        if holding is None:
            raise ValueError(f"{symbol} is not in the portfolio.")

        action = transaction.action.upper()

        if action == "BUY":
            holding.shares += transaction.shares

        elif action == "SELL":
            if transaction.shares > holding.shares:
                raise ValueError(
                    f"Cannot sell {transaction.shares:.2f} shares "
                    f"of {symbol}; only {holding.shares:.2f} shares "
                    "are currently held."
                )

            holding.shares -= transaction.shares

        transaction.action = action
        transaction.symbol = symbol

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

            if transaction.action.upper() == "BUY":
                balance += transaction.shares

            elif transaction.action.upper() == "SELL":
                balance -= transaction.shares

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

                action = transaction.action.upper()

                if action == "BUY":
                    shares += transaction.shares

                elif action == "SELL":
                    shares -= transaction.shares

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

    def summary(self) -> None:

        print()

        print(self.name)

        print("-" * 40)

        for holding in self.holdings:

            print(f"{holding.fund.symbol:8}{holding.allocation:6.1f}%")

        print("-" * 40)

        print(f"Total{'':3}{self.total_allocation:6.1f}%")
