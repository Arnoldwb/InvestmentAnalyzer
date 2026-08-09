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

            monthly = fund.monthly_returns()
            fund_returns[fund.symbol] = monthly


        insufficient_history = []

        for holding in self.portfolio.holdings:
            fund = holding.fund
            monthly = fund_returns[fund.symbol]

            if len(monthly) < 24:
                if fund.first_date is not None and fund.last_date is not None:
                    days = (fund.last_date - fund.first_date).days
                    months = days / 30.4375
                    coverage = f"approximately {months:.1f} months"
                else:
                    coverage = "insufficient historical coverage"

                insufficient_history.append(
                    f"{fund.symbol}: {coverage} available; "
                    "at least 24 months are required."
                )

        if insufficient_history:
            details = "\n".join(
                f"• {message}"
                for message in insufficient_history
            )

            raise ValueError(
                "Insufficient historical data for portfolio analysis.\n\n"
                f"{details}\n\n"
                "Please import additional historical data for "
                "the fund(s) listed above."
            )

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

    def growth_index(self, initial_value: float = 1.0) -> pd.Series:
        """
        Calculate compounded portfolio growth.
        """

        returns = self.monthly_returns()

        return initial_value * (1.0 + returns).cumprod()

    def cagr(self) -> float:
        """
        Calculate compound annual growth rate from monthly returns.
        """

        returns = self.monthly_returns()

        months = len(returns)

        if months == 0:
            return 0.0

        ending_value = (1.0 + returns).prod()

        years = months / 12.0

        return ending_value ** (1.0 / years) - 1.0

    def annualized_return(self) -> float:
        """
        Calculate annualized return from average monthly return.
        """

        returns = self.monthly_returns()

        return (1.0 + returns.mean()) ** 12 - 1.0

    def annualized_volatility(self) -> float:
        """
        Calculate annualized volatility.
        """

        returns = self.monthly_returns()

        return returns.std() * (12**0.5)

    def drawdown_series(self) -> pd.Series:
        """
        Calculate portfolio drawdown for every month.

        Drawdown measures the percentage decline from the
        portfolio's previous high-water mark.
        """

        growth = self.growth_index()

        running_peak = growth.cummax()

        drawdown = growth / running_peak - 1.0

        drawdown.name = "Drawdown"

        return drawdown

    def drawdown_episodes(self) -> list[dict]:
        """
        Identify completed portfolio drawdown episodes.

        Each episode begins at a portfolio peak, reaches a bottom,
        and ends when the portfolio regains the previous peak.
        """

        growth = self.growth_index()

        episodes = []

        peak_date = growth.index[0]
        peak_value = growth.iloc[0]

        in_drawdown = False
        bottom_date = None
        bottom_value = None

        for date, value in growth.iloc[1:].items():

            if value >= peak_value:

                if in_drawdown:
                    decline = bottom_value / peak_value - 1.0

                    episodes.append(
                        {
                            "peak_date": peak_date,
                            "bottom_date": bottom_date,
                            "recovery_date": date,
                            "decline": decline,
                            "days_to_bottom": (bottom_date - peak_date).days,
                            "days_bottom_to_recovery": (date - bottom_date).days,
                            "days_to_recovery": (date - peak_date).days,
                        }
                    )

                    in_drawdown = False
                    bottom_date = None
                    bottom_value = None

                peak_date = date
                peak_value = value

            else:
                if not in_drawdown:
                    in_drawdown = True
                    bottom_date = date
                    bottom_value = value

                elif value < bottom_value:
                    bottom_date = date
                    bottom_value = value

        return episodes

    def major_drawdowns(self, threshold: float = 0.10) -> list[dict]:
        """
        Return completed drawdown episodes whose decline
        is at least the specified threshold.

        Example:
        threshold=0.10 means declines of 10% or greater.
        """

        if threshold <= 0:
            raise ValueError("Drawdown threshold must be greater than zero.")

        episodes = self.drawdown_episodes()

        return [episode for episode in episodes if episode["decline"] <= -threshold]

    def stress_interpretation(self, threshold: float = 0.10) -> dict:
        """
        Return plain-language interpretation of major historical drawdowns.
        """

        episodes = self.major_drawdowns(threshold)

        if not episodes:
            return {
                "summary": (
                    f"The portfolio had no completed drawdowns of "
                    f"{threshold:.0%} or greater."
                )
            }

        worst = min(
            episodes,
            key=lambda episode: episode["decline"],
        )

        largest_recovery = max(
            episodes,
            key=lambda episode: episode["days_to_recovery"],
        )

        return {
            "count": (
                f"The portfolio experienced {len(episodes)} completed "
                f"drawdowns of {threshold:.0%} or greater."
            ),
            "worst": (
                f"The largest decline was {abs(worst['decline']):.2%}, "
                f"from the {worst['peak_date'].strftime('%B %Y')} peak "
                f"to the {worst['bottom_date'].strftime('%B %Y')} bottom."
            ),
            "worst_recovery": (
                f"That decline required {worst['days_to_recovery']:,} days "
                f"from peak to full recovery, including "
                f"{worst['days_bottom_to_recovery']:,} days after "
                f"the portfolio reached its bottom."
            ),
            "longest_recovery": (
                f"The longest peak-to-recovery period among these major "
                f"drawdowns was {largest_recovery['days_to_recovery']:,} "
                f"days."
            ),
        }

    def max_drawdown(self) -> float:
        """
        Calculate maximum portfolio drawdown.
        """

        return self.drawdown_series().min()

    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Calculate annualized Sharpe ratio.

          risk_free_rate is expressed as an annual decimal.
          Example: 0.04 represents 4%.
        """

        annual_return = self.annualized_return()
        volatility = self.annualized_volatility()

        if volatility == 0:
            return 0.0

        return (annual_return - risk_free_rate) / volatility

    def interpretation(self) -> dict:
        """
        Return plain-language interpretations of portfolio statistics.
        """

        cagr = self.cagr()
        volatility = self.annualized_volatility()
        drawdown = self.max_drawdown()
        sharpe = self.sharpe_ratio()

        return {
            "growth": (
                f"The portfolio produced a {cagr:.2%} "
                "compound annual growth rate over the analysis period."
            ),
            "risk": (f"Annualized volatility was {volatility:.2%}."),
            "drawdown": (
                f"The largest historical decline from a portfolio peak "
                f"was {abs(drawdown):.2%}."
            ),
            "risk_adjusted": (
                f"The portfolio's Sharpe ratio was {sharpe:.2f} "
                "using a 0% risk-free rate assumption."
            ),
        }
