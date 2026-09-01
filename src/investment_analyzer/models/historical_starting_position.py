from dataclasses import dataclass
from datetime import date


@dataclass
class HistoricalStartingPosition:
    """
    Represents a known share position that existed at the
    beginning of a portfolio's reliable transaction history.

    This is a starting position, not a transaction. In particular,
    it does not imply that the shares were purchased on this date
    or that a purchase price is known.
    """

    date: date
    symbol: str
    shares: float
    source: str = ""
