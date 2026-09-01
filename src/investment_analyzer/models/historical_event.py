from dataclasses import dataclass
from datetime import date


@dataclass
class HistoricalEvent:
    """
    Represents an investment-related event used to reconstruct
    historical portfolio positions and values.
    """

    date: date
    symbol: str
    event_type: str
    shares: float = 0.0
    price: float = 0.0
    amount: float = 0.0
    note: str = ""
