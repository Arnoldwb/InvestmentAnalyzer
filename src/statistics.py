import numpy as np


def cagr(df):
    start = df["Adj Close"].iloc[0]
    end = df["Adj Close"].iloc[-1]

    years = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25

    return (end / start) ** (1 / years) - 1


def max_drawdown(df):
    """Maximum drawdown as a percentage."""
    prices = df["Adj Close"]

    running_max = prices.cummax()

    drawdown = (prices - running_max) / running_max

    return drawdown.min()


def yearly_returns(df):

    """Calculate calendar-year returns."""

    yearly_prices = (

        df.set_index("Date")["Adj Close"]

          .resample("YE")

          .last()

    )

    return yearly_prices.pct_change().dropna()


def best_year(df):
    """Best calendar year return."""
    return yearly_returns(df).max()


def worst_year(df):
    """Worst calendar year return."""
    return yearly_returns(df).min()


def positive_years(df):
    """Number of positive calendar years."""
    return (yearly_returns(df) > 0).sum()


def negative_years(df):
    """Number of negative calendar years."""
    return (yearly_returns(df) < 0).sum()


def fund_statistics(monthly_returns):
    """
    Calculate statistics from a Series of monthly returns.
    """

    stats = {}

    stats["Months"] = len(monthly_returns)

    stats["Average Monthly Return"] = monthly_returns.mean()

    # Annualized return (compound)
    growth = (1 + monthly_returns).prod()
    years = len(monthly_returns) / 12

    stats["Annualized Return"] = growth ** (1 / years) - 1

    # Annualized volatility
    stats["Annualized Volatility"] = monthly_returns.std() * np.sqrt(12)

    stats["Best Month"] = monthly_returns.max()
    stats["Worst Month"] = monthly_returns.min()

    stats["Positive Months"] = (monthly_returns > 0).sum()
    stats["Negative Months"] = (monthly_returns < 0).sum()

    return stats