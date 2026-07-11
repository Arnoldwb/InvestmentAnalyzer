"""
Fund object for the Investment Analyzer.

A Fund encapsulates all information and calculations for a single mutual fund.
"""

from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd


@dataclass
class Fund:
    symbol: str
    data: pd.DataFrame = field(default_factory=pd.DataFrame)

    def load_data(self, data_folder="../data"):
        """
        Load the CSV for this fund.
        """

        csv_file = Path(data_folder) / f"{self.symbol}.csv"

        if not csv_file.exists():
            raise FileNotFoundError(csv_file)

        self.data = pd.read_csv(csv_file)

        self.data.columns = [c.strip() for c in self.data.columns]

        self.data["Date"] = pd.to_datetime(self.data["Date"])

        self.data["Adj Close"] = pd.to_numeric(
            self.data["Adj Close"],
            errors="coerce"
        )

        self.data = (
            self.data
            .dropna(subset=["Adj Close"])
            .sort_values("Date")
            .reset_index(drop=True)
        )

        return self

    @property
    def current_price(self):
        return float(self.data["Adj Close"].iloc[-1])

    @property
    def first_price(self):
        return float(self.data["Adj Close"].iloc[0])

    @property
    def first_date(self):
        return self.data["Date"].iloc[0]

   @property
def number_of_days(self):
    return (self.last_date - self.first_date).days


def monthly_returns(self):
    """
    Return monthly percentage returns.
    """

    prices = (
        self.data
        .set_index("Date")["Adj Close"]
        .resample("ME")
        .last()
    )

    return prices.pct_change().dropna()



def monthly_returns(self):
    """
    Return monthly percentage returns.
    """

    prices = (
        self.data
        .set_index("Date")["Adj Close"]
        .resample("ME")
        .last()
    )

    return prices.pct_change().dropna()

def yearly_returns(self):
    """
    Return yearly percentage returns.
    """

    prices = (
        self.data
        .set_index("Date")["Adj Close"]
        .resample("YE")
        .last()
    )

    return prices.pct_change().dropna()

def cagr(self):
    """
    Compound Annual Growth Rate.
    """

    years = self.number_of_days / 365.25

    if years <= 0:
        return 0.0

    return (
        (self.current_price / self.first_price) ** (1 / years)
        - 1
    )
def __len__(self):
    return len(self.data)


def __repr__(self):
    ...
def __len__(self):
    return len(self.data)

def __repr__(self):
    ...