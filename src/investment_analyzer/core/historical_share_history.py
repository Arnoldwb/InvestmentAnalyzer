from collections import defaultdict

import pandas as pd

from investment_analyzer.models.historical_event import HistoricalEvent
from investment_analyzer.models.historical_starting_position import (
    HistoricalStartingPosition,
)


def reconstruct_share_history(
    starting_positions: list[HistoricalStartingPosition],
    events: list[HistoricalEvent],
) -> pd.DataFrame:
    """
    Reconstruct the chronological share balance of each security.

    Starting positions establish the known opening share balances.
    Historical events then modify those balances chronologically.

    Returns a DataFrame with one row for each date/security combination
    at which the reconstructed share balance is established or changed.

    This function handles shares only. Prices, dollar values, cash flows,
    and investment performance are calculated separately.
    """

    shares = defaultdict(float)
    rows = []

    # Establish the starting balances in chronological order.
    for position in sorted(starting_positions, key=lambda p: p.date):
        shares[position.symbol] += position.shares

        rows.append(
            {
                "Date": position.date,
                "Symbol": position.symbol,
                "Shares": shares[position.symbol],
            }
        )

    # Apply historical events chronologically.
    ordered_events = sorted(events, key=lambda event: event.date)

    for event in ordered_events:
        if event.event_type in {"BUY", "REINVEST", "ADD"}:
            shares[event.symbol] += event.shares

        elif event.event_type in {"SELL", "REMOVE"}:
            shares[event.symbol] -= event.shares

        else:
            continue

        rows.append(
            {
                "Date": event.date,
                "Symbol": event.symbol,
                "Shares": shares[event.symbol],
            }
        )

    history = pd.DataFrame(rows)

    if history.empty:
        return pd.DataFrame(
            columns=["Date", "Symbol", "Shares"]
        )

    history["Date"] = pd.to_datetime(history["Date"])

    return (
        history
        .sort_values(["Date", "Symbol"])
        .reset_index(drop=True)
    )
