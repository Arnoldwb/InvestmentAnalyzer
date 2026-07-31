from dataclasses import dataclass

from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.models.portfolio import Portfolio


@dataclass
class PortfolioComparator:
    """
    Compares two portfolios using the same performance statistics.
    """

    portfolio_a: Portfolio
    portfolio_b: Portfolio

    def statistics(self, portfolio: Portfolio) -> dict:
        analyzer = PortfolioAnalyzer(portfolio)
        growth = analyzer.growth_index(10000)

        return {
            "name": portfolio.name,
            "cagr": analyzer.cagr(),
            "annualized_return": analyzer.annualized_return(),
            "volatility": analyzer.annualized_volatility(),
            "max_drawdown": analyzer.max_drawdown(),
            "sharpe": analyzer.sharpe_ratio(),
            "ending_value": growth.iloc[-1],
        }

    def compare(self) -> dict:
        """
        Return performance statistics for both portfolios.
        """

        return {
            "portfolio_a": self.statistics(self.portfolio_a),
            "portfolio_b": self.statistics(self.portfolio_b),
        }
