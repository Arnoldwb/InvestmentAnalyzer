from dataclasses import dataclass
from datetime import date

from .historical_event import HistoricalEvent


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
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    CASH_INTEREST = "CASH INTEREST"
    CASH_ADJUSTMENT = "CASH ADJUSTMENT"


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

    def to_historical_event(self) -> HistoricalEvent:
        """
        Convert this transaction into a HistoricalEvent.

        The historical reconstruction engine uses the event's
        share effect. Price and amount are preserved for future
        historical cash-flow and performance analysis.
        """

        event_type_map = {
            TransactionAction.BUY: "BUY",
            TransactionAction.SELL: "SELL",
            TransactionAction.REINVEST_DIVIDEND: "REINVEST",
            TransactionAction.REINVEST_CAPITAL_GAIN: "REINVEST",
            TransactionAction.ADD_SHARES: "ADD",
            TransactionAction.REMOVE_SHARES: "REMOVE",
        }

        event_type = event_type_map.get(self.action)

        if event_type is None:
            raise ValueError(
                f"Transaction action '{self.action}' cannot be converted "
                "to a historical share event."
            )

        return HistoricalEvent(
            date=self.date,
            symbol=self.symbol,
            event_type=event_type,
            shares=self.shares,
            price=self.price,
            amount=self.amount,
            note=self.note,
        )
