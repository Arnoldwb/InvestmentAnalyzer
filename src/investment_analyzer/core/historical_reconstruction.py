from collections import defaultdict

from investment_analyzer.models.historical_event import HistoricalEvent
from investment_analyzer.models.historical_starting_position import (
    HistoricalStartingPosition,
)


def reconstruct_shares(
    starting_positions: list[HistoricalStartingPosition],
    events: list[HistoricalEvent],
) -> dict[str, float]:
    """
    Reconstruct the ending share balance for each security.

    Starting positions establish the known opening share balances.
    Historical events then modify those balances.

    This function intentionally handles shares only. Dollar values,
    cash flows, and investment performance are calculated separately.
    """

    shares = defaultdict(float)

    for position in starting_positions:
        shares[position.symbol] += position.shares

    ordered_events = sorted(events, key=lambda event: event.date)

    for event in ordered_events:
        if event.event_type in {"BUY", "REINVEST", "ADD"}:
            shares[event.symbol] += event.shares

        elif event.event_type in {"SELL", "REMOVE"}:
            shares[event.symbol] -= event.shares

    return dict(shares)
