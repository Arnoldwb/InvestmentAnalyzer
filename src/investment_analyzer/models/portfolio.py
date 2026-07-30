from dataclasses import dataclass, field

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

    holdings: dict[str, float] = field(default_factory=dict)

    def add_fund(self, symbol: str, allocation: float):

        """

        Add or update a fund allocation.

        """

        symbol = symbol.upper()

        if allocation <= 0:

            raise ValueError("Allocation must be greater than zero.")

        self.holdings[symbol] = allocation

    @property

    def total_allocation(self):

        return sum(self.holdings.values())

    def validate(self):

        """

        Ensure allocations total 100%.

        """

        total = self.total_allocation

        if abs(total - 100.0) > 0.01:

            raise ValueError(

                f"Portfolio allocations total {total:.2f}%, not 100%."

            )

        return True

    def summary(self):

        print()

        print(self.name)

        print("-" * 40)

        for symbol, allocation in self.holdings.items():

            print(f"{symbol:8} {allocation:6.1f}%")

        print("-" * 40)

        print(f"Total    {self.total_allocation:6.1f}%")