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

    Placeholder rows become historical starting positions.
    Investment and share-changing rows become HistoricalEvent objects.

    Cash and income-only rows are currently ignored because this
    importer is initially concerned only with share reconstruction.
    """

    data = pd.read_csv(csv_file)

    starting_positions = []
    events = []

    security_name_map = {
        "Vanguard Wellington Fund Admiral Shares": "Vanguard Wellington Admiral",
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
            shares_match = re.search(
                r"([+-]?\d[\d,]*\.?\d*)\s+shares",
                description,
                re.IGNORECASE,
            )

            if shares_match:
                starting_positions.append(
                    HistoricalStartingPosition(
                        date=event_date,
                        symbol=security,
                        shares=abs(float(shares_match.group(1).replace(",", ""))),
                        source="Vanguard Placeholder",
                    )
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

        shares = abs(float(shares_match.group(1).replace(",", "")))

        price_match = re.search(
            r"@\s*\$?([\d,]+(?:\.\d+)?)",
            description,
            re.IGNORECASE,
        )

        price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

        transaction_amount = float(amount) if pd.notna(amount) else 0.0

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
    return starting_positions, events
