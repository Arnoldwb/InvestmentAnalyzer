"""
Preview automatic fund-data updates from Tiingo.

This module is initially read-only. It does not modify fund CSV files.
"""

from dataclasses import dataclass
from datetime import timedelta

import pandas as pd

from investment_analyzer.core.tiingo_client import TiingoClient
from investment_analyzer.models.fund import Fund


@dataclass
class UpdatePreview:
    """
    Summary of a prospective Tiingo fund-data update.
    """

    symbol: str
    current_last_date: pd.Timestamp
    tiingo_last_date: pd.Timestamp | None
    new_rows: int
    prices: list[dict]

    @property
    def update_available(self) -> bool:
        return self.new_rows > 0


class FundDataUpdater:
    """
    Determine whether newer Tiingo data is available for a fund.

    Preview operations do not modify the existing CSV file.
    """

    def __init__(self, client: TiingoClient | None = None):
        self.client = client or TiingoClient()

    def preview_update(self, symbol: str) -> UpdatePreview:
        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Fund symbol cannot be empty."
            )

        fund = Fund(symbol).load_data()

        current_last_date = pd.Timestamp(
            fund.last_date
        ).normalize()

        start_date = (
            current_last_date
            + timedelta(days=1)
        ).date()

        metadata = self.client.get_metadata(symbol)

        tiingo_end = metadata.get("endDate")

        tiingo_last_date = (
            pd.Timestamp(tiingo_end).normalize()
            if tiingo_end
            else None
        )

        if (
            tiingo_last_date is None
            or tiingo_last_date <= current_last_date
        ):
            return UpdatePreview(
                symbol=symbol,
                current_last_date=current_last_date,
                tiingo_last_date=tiingo_last_date,
                new_rows=0,
                prices=[],
            )

        prices = self.client.get_prices(
            symbol,
            start_date=start_date,
            end_date=tiingo_last_date.date(),
        )

        # Defensive filtering: only accept records later
        # than the existing fund's latest usable date.
        new_prices = []

        for row in prices:
            row_date = pd.Timestamp(
                row["date"]
            ).tz_localize(None).normalize()

            if row_date > current_last_date:
                new_prices.append(row)

        return UpdatePreview(
            symbol=symbol,
            current_last_date=current_last_date,
            tiingo_last_date=tiingo_last_date,
            new_rows=len(new_prices),
            prices=new_prices,
        )
