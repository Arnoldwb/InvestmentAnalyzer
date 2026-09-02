import re

import pandas as pd

from investment_analyzer.models.historical_event import HistoricalEvent
from investment_analyzer.models.historical_starting_position import (
    HistoricalStartingPosition,
)


def import_vanguard_history(
    csv_file,
) -> tuple[
    list[HistoricalStartingPosition],
    list[HistoricalEvent],
]:
    """
    Import Vanguard historical activity from a Quicken CSV export.

    Quicken Placeholder rows represent share-balance adjustments rather
    than ordinary investment transactions. The importer uses the
    Placeholder target balance to determine whether an unaccounted-for
    historical starting position is required.

    Same-day ADD/REMOVE pairs for the same normalized security are treated
    as Quicken security-name/reconciliation changes rather than economic
    share transactions.
    """

    data = pd.read_csv(csv_file)

    starting_positions = []
    events = []
    placeholders = []

    security_name_map = {
        "Vanguard Wellington Fund Admiral Shares":
            "Vanguard Wellington Admiral",
    }

    for _, row in data.iterrows():
        if pd.isna(row.get("Date")) or pd.isna(row.get("Type")):
            continue

        event_date = pd.to_datetime(row["Date"]).date()
        event_type = str(row["Type"]).strip()
        security = str(row.get("Security/Payee", "")).strip()
        description = str(row.get("Description/Category", "")).strip()

        if not security or security == "nan":
            continue

        security = security_name_map.get(security, security)

        amount = pd.to_numeric(
            str(row.get("Amount", "")).replace(",", ""),
            errors="coerce",
        )

        if event_type == "Placeholder":
            target_match = re.search(
                r"([+-]?\d[\d,]*\.?\d*)\s+shares\s*"
                r"\(to reach\s+([+-]?\d[\d,]*\.?\d*)\s+"
                r"on\s+(\d{1,2}/\d{1,2}/\d{2,4})\)",
                description,
                re.IGNORECASE,
            )

            if target_match:
                target_shares = float(
                    target_match.group(2).replace(",", "")
                )
                target_date = pd.to_datetime(
                    target_match.group(3)
                ).date()

                placeholders.append(
                    {
                        "date": event_date,
                        "symbol": security,
                        "target_date": target_date,
                        "target_shares": target_shares,
                    }
                )

            continue

        if event_type not in {
            "Buy",
            "Sell",
            "Reinvest Dividend",
            "Add Shares",
            "Remove Shares",
        }:
            continue

        shares_match = re.search(
            r"([+-]?\d[\d,]*\.?\d*)\s+shares",
            description,
            re.IGNORECASE,
        )

        if not shares_match:
            continue

        shares = abs(
            float(shares_match.group(1).replace(",", ""))
        )

        price_match = re.search(
            r"@\s*\$?([\d,]+(?:\.\d+)?)",
            description,
            re.IGNORECASE,
        )

        price = (
            float(price_match.group(1).replace(",", ""))
            if price_match
            else 0.0
        )

        transaction_amount = (
            float(amount)
            if pd.notna(amount)
            else 0.0
        )

        mapped_type = {
            "Buy": "BUY",
            "Sell": "SELL",
            "Reinvest Dividend": "REINVEST",
            "Add Shares": "ADD",
            "Remove Shares": "REMOVE",
        }[event_type]

        events.append(
            HistoricalEvent(
                date=event_date,
                symbol=security,
                event_type=mapped_type,
                shares=shares,
                price=price,
                amount=transaction_amount,
                note=f"Vanguard {event_type}",
            )
        )

    # Quicken may represent a security-name change as a same-day
    # REMOVE/ADD pair. When the normalized security is the same and
    # the share counts are effectively equal, this is not an economic
    # change in the holding.
    filtered_events = []
    rename_pairs = set()

    for index, event in enumerate(events):
        if event.event_type != "REMOVE":
            continue

        for other_index, other_event in enumerate(events):
            if other_index == index:
                continue

            if (
                other_event.date == event.date
                and other_event.symbol == event.symbol
                and other_event.event_type == "ADD"
                and abs(other_event.shares - event.shares) < 0.01
            ):
                rename_pairs.add(index)
                rename_pairs.add(other_index)
                break

    for index, event in enumerate(events):
        if index not in rename_pairs:
            filtered_events.append(event)

    events = filtered_events

    # Resolve Quicken Placeholder balances.
    #
    # The Placeholder target represents the number of shares Quicken
    # expected to hold on the stated target date. Determine how many
    # shares are already accounted for by actual transactions after
    # the Placeholder date and through that target date. Any remaining
    # difference is the missing historical starting position.
    for placeholder in placeholders:
        net_change = 0.0

        for event in events:
            if event.symbol != placeholder["symbol"]:
                continue

            if event.date <= placeholder["date"]:
                continue

            if event.date > placeholder["target_date"]:
                continue

            if event.event_type in {"BUY", "REINVEST", "ADD"}:
                net_change += event.shares
            elif event.event_type in {"SELL", "REMOVE"}:
                net_change -= event.shares

        opening_shares = (
            placeholder["target_shares"] - net_change
        )

        if opening_shares > 0.0005:
            starting_positions.append(
                HistoricalStartingPosition(
                    date=placeholder["date"],
                    symbol=placeholder["symbol"],
                    shares=opening_shares,
                    source="Vanguard Placeholder Reconciliation",
                )
            )

    return starting_positions, events
