from dataclasses import dataclass
from datetime import date


class TransactionAction:
    """Standard transaction action names."""

    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    REINVEST_DIVIDEND = "REINVEST DIVIDEND"
    CAPITAL_GAIN = "CAPITAL GAIN"
    REINVEST_CAPITAL_GAIN = "REINVEST CAPITAL GAIN"
    MANAGEMENT_FEE = "MANAGEMENT FEE"
    ADD_SHARES = "ADD SHARES"
    REMOVE_SHARES = "REMOVE SHARES"


@dataclass
class Transaction:
    """
    Represents one transaction for a fund.

    Share-based transactions use shares and price.
    Cash-only transactions use amount.
    """

    date: date
    symbol: str
    action: str
    shares: float
    price: float
    note: str = ""
    amount: float = 0.0

    @property
    def value(self) -> float:
        """Return the dollar value of the transaction."""

        if self.amount != 0.0:
            return self.amount

        return self.shares * self.price
