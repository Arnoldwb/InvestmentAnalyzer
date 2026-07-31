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

    def interpretation(self) -> dict:
        """
        Return plain-language interpretations of the comparison.
        """

        results = self.compare()

        a = results["portfolio_a"]
        b = results["portfolio_b"]

        if a["cagr"] >= b["cagr"]:
            growth_winner = a
            growth_other = b
        else:
            growth_winner = b
            growth_other = a

        if a["volatility"] <= b["volatility"]:
            risk_winner = a
            risk_other = b
        else:
            risk_winner = b
            risk_other = a

        if a["max_drawdown"] >= b["max_drawdown"]:
            drawdown_winner = a
            drawdown_other = b
        else:
            drawdown_winner = b
            drawdown_other = a

        if a["sharpe"] >= b["sharpe"]:
            sharpe_winner = a
            sharpe_other = b
        else:
            sharpe_winner = b
            sharpe_other = a

        if a["ending_value"] >= b["ending_value"]:
            value_winner = a
            value_other = b
        else:
            value_winner = b
            value_other = a

        return {
            "growth": (
                f"{growth_winner['name']} had the higher CAGR: "
                f"{growth_winner['cagr']:.2%} versus "
                f"{growth_other['cagr']:.2%}."
            ),
            "risk": (
                f"{risk_winner['name']} had the lower annualized volatility: "
                f"{risk_winner['volatility']:.2%} versus "
                f"{risk_other['volatility']:.2%}."
            ),
            "drawdown": (
                f"{drawdown_winner['name']} had the smaller maximum drawdown: "
                f"{abs(drawdown_winner['max_drawdown']):.2%} versus "
                f"{abs(drawdown_other['max_drawdown']):.2%}."
            ),
            "risk_adjusted": (
                f"{sharpe_winner['name']} had the higher Sharpe ratio: "
                f"{sharpe_winner['sharpe']:.2f} versus "
                f"{sharpe_other['sharpe']:.2f}."
            ),
            "ending_value": (
                f"{value_winner['name']} produced the higher ending value: "
                f"${value_winner['ending_value']:,.2f} versus "
                f"${value_other['ending_value']:,.2f}."
            ),
        }
