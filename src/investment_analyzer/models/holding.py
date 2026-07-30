from dataclasses import dataclass

from .fund import Fund

@dataclass

class Holding:

    """

    Represents one holding in a portfolio.

    """

    fund: Fund

    allocation: float

    @property

    def symbol(self):

        return self.fund.symbol