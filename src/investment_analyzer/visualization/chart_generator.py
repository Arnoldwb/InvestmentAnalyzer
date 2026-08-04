from matplotlib.figure import Figure

from investment_analyzer.analysis.portfolio_analyzer import (
    PortfolioAnalyzer,
)


class ChartGenerator:
    """
    Create charts for Investment Analyzer.
    """

    def portfolio_growth_chart(
        self,
        portfolio,
        initial_value: float = 10000.0,
    ) -> Figure:
        """
        Create a Growth of Investment chart for a portfolio.
        """

        analyzer = PortfolioAnalyzer(portfolio)
        growth = analyzer.growth_index(initial_value)

        figure = Figure(figsize=(9, 5.5))
        axes = figure.subplots()

        axes.plot(
            growth.index,
            growth.values,
            linewidth=2,
        )

        axes.set_title(
            f"{portfolio.name} — Growth of ${initial_value:,.0f}"
        )
        axes.set_xlabel("Date")
        axes.set_ylabel("Portfolio Value ($)")
        axes.grid(True)

        axes.yaxis.set_major_formatter(
            lambda value, position: f"${value:,.0f}"
        )

        figure.tight_layout()

        return figure

    def portfolio_drawdown_chart(self, portfolio) -> Figure:
        """
        Create a historical drawdown chart for a portfolio.
        """

        analyzer = PortfolioAnalyzer(portfolio)
        drawdown = analyzer.drawdown_series() * 100.0

        figure = Figure(figsize=(9, 5.5))
        axes = figure.subplots()

        axes.plot(
            drawdown.index,
            drawdown.values,
            linewidth=2,
        )

        axes.axhline(
            0.0,
            linewidth=1,
        )

        axes.set_title(
            f"{portfolio.name} — Drawdown History"
        )
        axes.set_xlabel("Date")
        axes.set_ylabel("Drawdown (%)")
        axes.grid(True)

        axes.yaxis.set_major_formatter(
            lambda value, position: f"{value:.0f}%"
        )

        figure.tight_layout()

        return figure
