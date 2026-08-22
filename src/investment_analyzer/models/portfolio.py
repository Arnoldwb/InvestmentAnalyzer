from dataclasses import dataclass, field

from .fund import Fund

from .holding import Holding


@dataclass
class Portfolio:
    """

    Represents a portfolio consisting of multiple funds.

    """

    name: str = "Portfolio"

    holdings: list[Holding] = field(default_factory=list)

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
            )
        )

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
