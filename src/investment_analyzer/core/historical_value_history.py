"""
Calculate daily historical holding values from reconstructed share history.
"""

import pandas as pd

from investment_analyzer.core.historical_security_mapping import (
    historical_security_to_symbol,
)
from investment_analyzer.models.fund import Fund


def calculate_historical_value_history(
    share_history: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate daily historical values for mapped securities.

    Share balances are carried forward from each historical share event
    until the next event. Historical prices come from the existing Fund
    price data.

    Returns a DataFrame containing:

        Date
        Symbol
        Shares
        Price
        Value

    Securities without a known local fund-symbol mapping are skipped.
    """

    if share_history.empty:
        return pd.DataFrame(
            columns=["Date", "Symbol", "Shares", "Price", "Value"]
        )

    history = share_history.copy()

    history["Date"] = pd.to_datetime(history["Date"]).astype(
        "datetime64[ns]"
    )

    results = []

    for security_name, security_history in history.groupby("Symbol"):
        symbol = historical_security_to_symbol(security_name)

        if symbol is None:
            continue

        fund = Fund(symbol).load_data()

        share_history_for_security = (
            security_history
            .sort_values("Date")
            [["Date", "Shares"]]
            .drop_duplicates(subset=["Date"], keep="last")
        )

        prices = (
            fund.data[["Date", "Adj Close"]]
            .rename(columns={"Adj Close": "Price"})
            .sort_values("Date")
            .copy()
        )

        prices["Date"] = pd.to_datetime(prices["Date"]).astype(
            "datetime64[ns]"
        )

        start_date = share_history_for_security["Date"].min()

        prices = prices[prices["Date"] >= start_date].copy()

        if prices.empty:
            continue

        daily = pd.merge_asof(
            prices,
            share_history_for_security,
            on="Date",
            direction="backward",
        )

        daily = daily.dropna(subset=["Shares"])

        daily["Symbol"] = symbol
        daily["Value"] = daily["Shares"] * daily["Price"]

        results.append(
            daily[
                ["Date", "Symbol", "Shares", "Price", "Value"]
            ]
        )

    if not results:
        return pd.DataFrame(
            columns=["Date", "Symbol", "Shares", "Price", "Value"]
        )

    return (
        pd.concat(results, ignore_index=True)
        .sort_values(["Date", "Symbol"])
        .reset_index(drop=True)
    )
