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

    def monthly_returns(self) -> pd.Series:
        """
        Return the portfolio's complete monthly return history.
        """

        analyzer = PortfolioAnalyzer(self.portfolio)

        return analyzer.monthly_returns()

    def returns_for_period(
        self,
        start_date: str,
        end_date: str,
    ) -> pd.Series:
        """
        Return portfolio monthly returns within a specified
        historical period.
        """

        returns = self.monthly_returns()

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
        before the first monthly return is applied.
        """

        returns = self.returns_for_period(
            start_date,
            end_date,
        )

        growth = (1.0 + returns).cumprod()

        total_return = growth.iloc[-1] - 1.0

        starting_date = (
            returns.index[0] - pd.offsets.MonthEnd(1)
        )

        growth_with_start = pd.concat(
            [
                pd.Series(
                    [1.0],
                    index=[starting_date],
                ),
                growth,
            ]
        )

        running_peak = growth_with_start.cummax()

        drawdown = (
            growth_with_start / running_peak - 1.0
        )

        return {
            "start_date": returns.index[0],
            "end_date": returns.index[-1],
            "months": len(returns),
            "total_return": total_return,
            "max_drawdown": drawdown.min(),
        }

    def analyze_scenario(
        self,
        scenario: dict,
    ) -> dict:
        """
        Analyze a named historical scenario definition.
        """

        result = self.analyze_period(
            scenario["start_date"],
            scenario["end_date"],
        )

        result["name"] = scenario["name"]
        result["description"] = scenario.get(
            "description",
            "",
        )

        return result

    def recovery_analysis(
        self,
        start_date: str,
        end_date: str,
    ) -> dict:
        """
        Analyze the peak, bottom, and subsequent recovery
        associated with a historical stress scenario.

        The peak and bottom are identified within the scenario
        window. Recovery may occur after the scenario window ends.
        """

        all_returns = self.monthly_returns()

        scenario_returns = self.returns_for_period(
            start_date,
            end_date,
        )

        starting_date = (
            scenario_returns.index[0]
            - pd.offsets.MonthEnd(1)
        )

        returns_from_start = all_returns.loc[
            all_returns.index
            >= scenario_returns.index[0]
        ]

        growth = (
            1.0 + returns_from_start
        ).cumprod()

        growth_with_start = pd.concat(
            [
                pd.Series(
                    [1.0],
                    index=[starting_date],
                ),
                growth,
            ]
        )

        scenario_growth = growth_with_start.loc[
            :scenario_returns.index[-1]
        ]

        peak_date = scenario_growth.idxmax()
        peak_value = scenario_growth.loc[peak_date]

        after_peak = scenario_growth.loc[peak_date:]

        bottom_date = after_peak.idxmin()
        bottom_value = after_peak.loc[bottom_date]

        decline = (
            bottom_value / peak_value - 1.0
        )

        after_bottom = growth_with_start.loc[
            bottom_date:
        ]

        recovery_values = after_bottom.loc[
            after_bottom >= peak_value
        ]

        recovery_date = (
            recovery_values.index[0]
            if not recovery_values.empty
            else None
        )

        result = {
            "peak_date": peak_date,
            "bottom_date": bottom_date,
            "decline": decline,
            "days_to_bottom": (
                bottom_date - peak_date
            ).days,
            "recovery_date": recovery_date,
        }

        if recovery_date is not None:
            result["days_bottom_to_recovery"] = (
                recovery_date - bottom_date
            ).days

            result["days_to_recovery"] = (
                recovery_date - peak_date
            ).days
        else:
            result["days_bottom_to_recovery"] = None
            result["days_to_recovery"] = None

        return result
