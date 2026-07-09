import pandas as pd

def monthly_returns(df):

    """

    Convert daily adjusted closing prices into monthly returns.

    """

    monthly_prices = (

        df.set_index("Date")["Adj Close"]

          .resample("ME")

          .last()

    )

    monthly_returns = monthly_prices.pct_change().dropna()

    return monthly_returns