from dataclasses import dataclass

import pandas as pd

from investment_analyzer.models.portfolio import Portfolio


@dataclass
class PortfolioAnalyzer:
    """
    Performs analysis on a Portfolio.
    """

    portfolio: Portfolio

    def summary(self):
        print()
        print("Portfolio Analysis")
        print("-" * 40)
        self.portfolio.summary()

    def monthly_returns(self) -> pd.Series:
        """
        Calculate weighted monthly returns for the portfolio.

        Only months for which every holding has return data
        are included.
        """

        self.portfolio.validate()

        fund_returns = {}

        for holding in self.portfolio.holdings:
            fund = holding.fund

            if fund.data.empty:
                fund.load_data()

            fund_returns[fund.symbol] = fund.monthly_returns()

        returns = pd.concat(
            fund_returns,
            axis=1,
            join="inner",
        ).dropna()

        if returns.empty:
            raise ValueError(
                "No common monthly return history exists for the portfolio."
            )

        portfolio_returns = pd.Series(
            0.0,
            index=returns.index,
            name="Portfolio",
        )

        for holding in self.portfolio.holdings:
            weight = holding.allocation / 100.0

            portfolio_returns += returns[holding.fund.symbol] * weight

        return portfolio_returns
