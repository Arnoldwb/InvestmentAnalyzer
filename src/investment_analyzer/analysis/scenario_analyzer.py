from dataclasses import dataclass

import pandas as pd

from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio


@dataclass
class ScenarioAnalyzer:
    """
    Analyze portfolio performance during specific historical periods.
    """

    portfolio: Portfolio

    def returns_for_period(
        self,
        start_date: str,
        end_date: str,
    ) -> pd.Series:
        """
        Return portfolio monthly returns within a specified
        historical period.
        """

        analyzer = PortfolioAnalyzer(self.portfolio)
        returns = analyzer.monthly_returns()

        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)

        if start > end:
            raise ValueError(
                "Scenario start date must be before the end date."
            )

        period_returns = returns.loc[
            (returns.index >= start) & (returns.index <= end)
        ]

        if period_returns.empty:
            raise ValueError(
                "No portfolio return data exists for this scenario period."
            )

        return period_returns

    def analyze_period(
        self,
        start_date: str,
        end_date: str,
    ) -> dict:
        """
        Analyze portfolio performance during a historical period.

        The scenario begins with a value of 1.0 immediately
        before the first monthly return is applied. This allows
        drawdown calculations to include losses occurring during
        the first month of the scenario.
        """

        returns = self.returns_for_period(start_date, end_date)

        growth = (1.0 + returns).cumprod()

        total_return = growth.iloc[-1] - 1.0

        starting_value = pd.Series(
            [1.0],
            index=[returns.index[0] - pd.offsets.MonthEnd(1)],
        )

        growth_with_start = pd.concat(
            [starting_value, growth]
        )

        running_peak = growth_with_start.cummax()

        drawdown = (
            growth_with_start / running_peak - 1.0
        )

        max_drawdown = drawdown.min()

        return {
            "start_date": returns.index[0],
            "end_date": returns.index[-1],
            "months": len(returns),
            "total_return": total_return,
            "max_drawdown": max_drawdown,
        }
