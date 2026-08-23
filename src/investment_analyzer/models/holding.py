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
    opening_shares: float | None = None

    @property
    def symbol(self):
        return self.fund.symbol

    @property
    def starting_shares(self) -> float:
        """
        Return the share balance that existed before
        transaction tracking began.
        """

        if self.opening_shares is None:
            return self.shares

        return self.opening_shares

    @property
    def current_price(self):
        return self.fund.current_price

    @property
    def current_value(self):
        return self.shares * self.current_price
