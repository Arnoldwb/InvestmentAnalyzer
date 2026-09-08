from dataclasses import dataclass
from datetime import date


@dataclass
class HistoricalStartingCash:
    """
    Represents a known cash balance that existed at the
    beginning of a portfolio's reliable transaction history.

    This is a starting balance, not a transaction. In particular,
    it does not imply that the cash was deposited on this date.
    """

    date: date
    amount: float
    source: str = ""
