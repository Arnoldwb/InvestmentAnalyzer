"""
Calculate daily historical portfolio values from holding values.
"""

import pandas as pd


def calculate_historical_portfolio_value(
    value_history: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate historical holding values into daily portfolio values.

    Returns a DataFrame containing:

        Date
        Portfolio Value
    """

    if value_history.empty:
        return pd.DataFrame(
            columns=["Date", "Portfolio Value"]
        )

    required_columns = {"Date", "Value"}

    missing = required_columns - set(value_history.columns)

    if missing:
        raise ValueError(
            f"Historical value history is missing columns: "
            f"{sorted(missing)}"
        )

    history = value_history.copy()

    history["Date"] = pd.to_datetime(history["Date"])

    portfolio_history = (
        history
        .groupby("Date", as_index=False)["Value"]
        .sum()
        .rename(columns={"Value": "Portfolio Value"})
        .sort_values("Date")
        .reset_index(drop=True)
    )

    return portfolio_history
