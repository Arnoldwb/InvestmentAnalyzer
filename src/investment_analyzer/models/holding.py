from dataclasses import dataclass

from .fund import Fund


@dataclass
class Holding:
    """
    Represents one holding in a portfolio.
    """

    fund: Fund
    allocation: float
    shares: float = 0.0

    @property
    def symbol(self):
        return self.fund.symbol

    @property
    def current_price(self):
        return self.fund.current_price

    @property
    def current_value(self):
        return self.shares * self.current_price
