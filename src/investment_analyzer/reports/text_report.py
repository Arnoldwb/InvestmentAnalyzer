from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer

from .base_report import BaseReport
from .report_builder import ReportBuilder


class TextReport(BaseReport):
    """
    Creates professional text reports.
    """

    def create_portfolio_report(self, portfolio):
        filename = self.report_path("PortfolioReport.txt")

        analyzer = PortfolioAnalyzer(portfolio)
        returns = analyzer.monthly_returns()
        growth = analyzer.growth_index(10000)

        builder = ReportBuilder()

        builder.title(
            "Investment Analyzer\n" "Version 3.4\n" "Portfolio Analysis Report"
        )

        builder.field("Generated:", self.timestamp)
        builder.blank()

        builder.field("Portfolio:", portfolio.name)
        builder.blank()

        builder.section("Holdings")

        for holding in portfolio.holdings:
            builder.field(holding.fund.symbol, f"{holding.allocation:.1f}%")

        builder.line("-" * 60)

        builder.field("Total Allocation", f"{portfolio.total_allocation:.1f}%")

        builder.blank()

        builder.section("Performance Statistics")

        first_month = returns.index.min().strftime("%b %Y")
        last_month = returns.index.max().strftime("%b %Y")

        builder.field("Analysis Period", f"{first_month} - {last_month}")
        builder.field("Months Analyzed", len(returns))
        builder.field("CAGR", f"{analyzer.cagr():.2%}")
        builder.field("Annualized Avg Return", f"{analyzer.annualized_return():.2%}")
        builder.field(
            "Annualized Volatility", f"{analyzer.annualized_volatility():.2%}"
        )
        builder.field("Maximum Drawdown", f"{analyzer.max_drawdown():.2%}")
        builder.field("Sharpe Ratio", f"{analyzer.sharpe_ratio():.2f}")

        builder.blank()

        builder.section("Growth of $10,000")

        builder.field("Beginning Value", "$10,000.00")
        builder.field("Ending Value", f"${growth.iloc[-1]:,.2f}")

        builder.blank()

        try:
            portfolio.validate()
            builder.field("Portfolio Validation", "PASSED")
        except ValueError:
            builder.field("Portfolio Validation", "FAILED")

        builder.save(filename)

        return filename
