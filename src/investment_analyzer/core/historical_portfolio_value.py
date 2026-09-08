"""
Calculate daily historical portfolio values from holding values.
"""

import pandas as pd


def calculate_historical_portfolio_value(
    value_history: pd.DataFrame,
    cash_history: pd.DataFrame | None = None,
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

    if cash_history is not None and not cash_history.empty:
        required_cash_columns = {"Date", "Cash"}
        missing_cash = required_cash_columns - set(cash_history.columns)

        if missing_cash:
            raise ValueError(
                f"Historical cash history is missing columns: "
                f"{sorted(missing_cash)}"
            )

        cash = cash_history.copy()

        cash["Date"] = pd.to_datetime(cash["Date"])

        cash = (
            cash
            .sort_values("Date")
            .drop_duplicates(subset=["Date"], keep="last")
        )

        portfolio_history = pd.merge_asof(
            portfolio_history.sort_values("Date"),
            cash[["Date", "Cash"]],
            on="Date",
            direction="backward",
        )

        portfolio_history = portfolio_history.dropna(subset=["Cash"])

        portfolio_history["Portfolio Value"] += portfolio_history["Cash"]

        portfolio_history = portfolio_history.drop(columns=["Cash"])

    return portfolio_history
