from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketCycle:
    """
    Represents one complete bull or bear market cycle.
    """

    cycle_type: str          # "Bull" or "Bear"

    start_date: datetime
    end_date: datetime

    start_price: float
    end_price: float

    @property
    def days(self):
        """Length of cycle in days."""
        return (self.end_date - self.start_date).days

    @property
    def percent_change(self):
        """Return percentage over the cycle."""
        return (
            (self.end_price - self.start_price)
            / self.start_price
            * 100
        )

    def summary(self):
        return {
            "Type": self.cycle_type,
            "Start": self.start_date.date(),
            "End": self.end_date.date(),
            "Days": self.days,
            "Return %": round(self.percent_change, 2),
        }