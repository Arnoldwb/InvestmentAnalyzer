from dataclasses import dataclass, field

from .fund import Fund

from .holding import Holding


@dataclass
class Portfolio:
    """

    Represents a portfolio consisting of multiple funds.

    Example:

        VWENX 40%

        VGSTX 30%

        VBIAX 20%

        VSMGX 10%

    """

    name: str = "Portfolio"

    holdings: list[Holding] = field(default_factory=list)

    def add_fund(self, symbol: str, allocation: float):
        """Add a fund to the portfolio."""

        if allocation <= 0:

            raise ValueError("Allocation must be greater than zero.")

        fund = Fund(symbol.upper())

        self.holdings.append(Holding(fund=fund, allocation=allocation))

    @property
    def number_of_holdings(self):

        return len(self.holdings)

    @property
    def total_allocation(self):

        return sum(h.allocation for h in self.holdings)

    def validate(self):
        """Ensure allocations total 100%."""

        total = self.total_allocation

        if abs(total - 100.0) > 0.01:

            raise ValueError(f"Portfolio allocations total {total:.2f}%, not 100%.")

        return True

    def summary(self):

        print()

        print(self.name)

        print("-" * 40)

        for holding in self.holdings:

            print(f"{holding.fund.symbol:8}{holding.allocation:6.1f}%")

        print("-" * 40)

        print(f"Total{'':3}{self.total_allocation:6.1f}%")
