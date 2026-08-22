from dataclasses import dataclass
from datetime import date


@dataclass
class Transaction:
    """
    Represents one buy or sell transaction for a fund.
    """

    date: date
    symbol: str
    action: str
    shares: float
    price: float
    note: str = ""

    @property
    def value(self) -> float:
        """Return the dollar value of the transaction."""

        return self.shares * self.price
