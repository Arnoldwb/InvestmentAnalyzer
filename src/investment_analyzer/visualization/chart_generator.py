from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import numpy as np

from investment_analyzer.analysis.portfolio_analyzer import (
    PortfolioAnalyzer,
)
from investment_analyzer.core.fund_metadata import get_fund_name


class ChartGenerator:
    """
    Create charts for Investment Analyzer.
    """

    def portfolio_growth_chart(
        self,  # Plot each individual fund's allocation-weighted growth.
        portfolio,
        initial_value: float = 10000.0,
    ) -> Figure:
        """
        Create a Growth of Investment chart for a portfolio,
        including allocation-weighted growth lines for each fund.
        """

        analyzer = PortfolioAnalyzer(portfolio)

        growth = analyzer.growth_index(initial_value)
        fund_growth = analyzer.fund_growth_indices(initial_value)

        # Add the investment's starting value immediately before
        # the first monthly return so the chart begins at the
        # requested initial investment.
        if not growth.empty:
            start_date = growth.index[0] - growth.index.freq

            growth.loc[start_date] = initial_value
            growth = growth.sort_index()

        figure = Figure(figsize=(9, 5.5))
        axes = figure.subplots()

        # Plot each individual fund's allocation-weighted growth.
        for holding in portfolio.holdings:
            symbol = holding.fund.symbol
            allocation = holding.allocation

            axes.plot(
                fund_growth.index,
                fund_growth[symbol],
                linewidth=1.0,
                alpha=0.8,
                label=(
                    f"{symbol} — " f"{get_fund_name(symbol)} — " f"{allocation:.1f}%"
                ),
            )

        # Plot the total portfolio on top of the individual funds.
        axes.plot(
            growth.index,
            growth.values,
            linewidth=2.5,
            label="Portfolio",
        )

        axes.set_title(f"{portfolio.name} — Growth of ${initial_value:,.0f}")
        axes.set_xlabel("Date")
        axes.set_ylabel("Portfolio Value ($)")
        axes.grid(True)

        axes.yaxis.set_major_formatter(lambda value, position: f"${value:,.0f}")

        axes.legend()

        figure.tight_layout()

        return figure

    def portfolio_monthly_returns_chart(self, portfolio) -> Figure:
        """
        Create a monthly portfolio returns chart.
        """

        analyzer = PortfolioAnalyzer(portfolio)
        returns = analyzer.monthly_returns() * 100.0

        figure = Figure(figsize=(9, 5.5))
        axes = figure.subplots()

        axes.bar(
            returns.index,
            returns.values,
            width=20,
        )

        axes.axhline(
            0.0,
            linewidth=1,
        )

        axes.set_title(f"{portfolio.name} — Monthly Returns")

        axes.set_xlabel("Date")
        axes.set_ylabel("Monthly Return (%)")
        axes.grid(
            True,
            axis="y",
        )

        axes.yaxis.set_major_formatter(lambda value, position: f"{value:.0f}%")

        figure.tight_layout()

        return figure

    def portfolio_allocation_chart(self, portfolio) -> Figure:
        """
        Create a portfolio allocation chart showing each fund
        sorted by allocation, with a different color for each fund.
        """

        holdings = sorted(
            portfolio.holdings,
            key=lambda holding: holding.allocation,
            reverse=True,
        )

        labels = [holding.fund.symbol for holding in holdings]

        allocations = [holding.allocation for holding in holdings]

        figure = Figure(figsize=(9, 5.5))
        axes = figure.subplots()

        # Different color for each fund.
        colors = [
            "#1f77b4",  # Blue
            "#d62728",  # Red
            "#9467bd",  # Purple
            "#8c564b",  # Brown
            "#2ca02c",  # Green
            "#ff7f0e",  # Orange
            "#17becf",  # Teal
            "#e377c2",  # Pink
            "#7f7f7f",  # Gray
            "#bcbd22",  # Olive
        ]

        # Keep bar thickness and spacing consistent
        # regardless of the number of funds.
        bar_height = 0.18
        center_spacing = 0.55

        y_positions = [index * center_spacing for index in range(len(labels))]

        bars = axes.barh(
            y_positions,
            allocations,
            height=bar_height,
            color=[colors[index % len(colors)] for index in range(len(labels))],
        )

        axes.set_yticks(y_positions)
        axes.set_yticklabels(labels)

        if y_positions:
            axes.set_ylim(
                -0.45,
                y_positions[-1] + 0.45,
            )

        # Put the largest allocation at the top.
        axes.invert_yaxis()

        axes.set_title(f"{portfolio.name} — Portfolio Allocation")
        axes.set_xlabel("Allocation (%)")
        axes.grid(
            True,
            axis="x",
        )

        axes.xaxis.set_major_formatter(lambda value, position: f"{value:.0f}%")

        for bar, allocation in zip(bars, allocations):
            axes.text(
                bar.get_width() + 0.5,
                bar.get_y() + bar.get_height() / 2,
                f"{allocation:.1f}%",
                va="center",
            )

        figure.tight_layout()

        return figure

    def monte_carlo_distribution_chart(
        self,
        ending_values,
        years: int,
        simulations: int,
        initial_value: float,
    ) -> Figure:
        """
        Create a readable Monte Carlo ending-value distribution chart.

        Shows the distribution of simulated ending values with
        percentile and mean markers.
        """

        percentile_10 = np.percentile(ending_values, 10)
        percentile_25 = np.percentile(ending_values, 25)
        median = np.percentile(ending_values, 50)
        percentile_75 = np.percentile(ending_values, 75)
        percentile_90 = np.percentile(ending_values, 90)
        mean = np.mean(ending_values)

        figure = Figure(figsize=(9, 5.5))
        axes = figure.subplots()

        # Histogram of simulated ending values.
        axes.hist(
            ending_values,
            bins=50,
            alpha=0.75,
            edgecolor="black",
            linewidth=0.5,
        )

        # Percentile marker definitions.
        markers = [
            (percentile_10, "10th Percentile", "#d62728"),
            (percentile_25, "25th Percentile", "#ff7f0e"),
            (median, "Median", "#2ca02c"),
            (percentile_75, "75th Percentile", "#1f4ed8"),
            (percentile_90, "90th Percentile", "#9467bd"),
        ]

        # Draw thicker dashed percentile lines.
        for value, label, color in markers:
            axes.axvline(
                value,
                color=color,
                linestyle="--",
                linewidth=2.5,
            )

        # Draw the mean line in black.
        axes.axvline(
            mean,
            color="black",
            linestyle="--",
            linewidth=2.5,
        )

        axes.set_title(
            "Monte Carlo Outcome Distribution",
            fontsize=14,
            fontweight="bold",
            pad=24,
        )

        axes.text(
            0.5,
            1.02,
            (
                f"{years} Years • "
                f"{simulations:,} Simulations • "
                f"Starting Value: ${initial_value:,.0f}"
            ),
            transform=axes.transAxes,
            ha="center",
            va="bottom",
            fontsize=10,
        )

        axes.set_xlabel("Ending Portfolio Value")
        axes.set_ylabel("Number of Simulations")

        axes.xaxis.set_major_formatter(
            lambda value, position: (
                f"${value / 1_000_000:.0f}M"
                if value >= 1_000_000
                else f"${value / 1_000:.0f}K"
            )
        )

        axes.grid(
            True,
            axis="y",
            alpha=0.3,
        )

        # ---------------------------------------------------------
        # Colored identifiers for the percentile information box.
        # ---------------------------------------------------------

        legend_colors = [
            "#d62728",
            "#ff7f0e",
            "#2ca02c",
            "#1f4ed8",
            "#9467bd",
            "black",
        ]

        legend_labels = [
            f"10th Percentile   ${percentile_10:,.0f}",
            f"25th Percentile   ${percentile_25:,.0f}",
            f"Median            ${median:,.0f}",
            f"75th Percentile   ${percentile_75:,.0f}",
            f"90th Percentile   ${percentile_90:,.0f}",
            f"Mean              ${mean:,.0f}",
        ]

        legend_handles = [
            Line2D(
                [0],
                [0],
                marker="s",
                linestyle="None",
                markerfacecolor=color,
                markeredgecolor=color,
                markersize=9,
            )
            for color in legend_colors
        ]

        axes.legend(
            legend_handles,
            legend_labels,
            loc="upper right",
            bbox_to_anchor=(0.98, 0.98),
            frameon=True,
            framealpha=0.92,
            fontsize=9,
            borderaxespad=0.5,
        )

        figure.tight_layout()

        return figure
