from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.analysis.portfolio_comparator import PortfolioComparator
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
        builder.section("Performance Interpretation")

        interpretation = analyzer.interpretation()

        builder.line("Growth:")
        builder.line(interpretation["growth"])
        builder.blank()

        builder.line("Risk:")
        builder.line(interpretation["risk"])
        builder.blank()

        builder.line("Drawdown:")
        builder.line(interpretation["drawdown"])
        builder.blank()

        builder.line("Risk-Adjusted Performance:")
        builder.line(interpretation["risk_adjusted"])

        builder.blank()
        try:
            portfolio.validate()
            builder.field("Portfolio Validation", "PASSED")
        except ValueError:
            builder.field("Portfolio Validation", "FAILED")

        builder.save(filename)

        return filename

    def create_comparison_report(self, portfolio_a, portfolio_b):
        """
        Create a side-by-side portfolio comparison report.
        """

        filename = self.report_path("PortfolioComparisonReport.txt")

        comparator = PortfolioComparator(
            portfolio_a,
            portfolio_b,
        )

        results = comparator.compare()

        a = results["portfolio_a"]
        b = results["portfolio_b"]

        builder = ReportBuilder()

        builder.title(
            "Investment Analyzer\n" "Version 3.5\n" "Portfolio Comparison Report"
        )

        builder.field("Generated:", self.timestamp)
        builder.blank()

        builder.line(f"{'Metric':<25}" f"{'Portfolio A':>17}" f"{'Portfolio B':>17}")

        builder.line("-" * 59)

        builder.line(f"{'CAGR':<25}" f"{a['cagr']:>16.2%}" f"{b['cagr']:>17.2%}")

        builder.line(
            f"{'Annualized Avg Return':<25}"
            f"{a['annualized_return']:>16.2%}"
            f"{b['annualized_return']:>17.2%}"
        )

        builder.line(
            f"{'Annualized Volatility':<25}"
            f"{a['volatility']:>16.2%}"
            f"{b['volatility']:>17.2%}"
        )

        builder.line(
            f"{'Maximum Drawdown':<25}"
            f"{a['max_drawdown']:>16.2%}"
            f"{b['max_drawdown']:>17.2%}"
        )

        builder.line(
            f"{'Sharpe Ratio':<25}" f"{a['sharpe']:>16.2f}" f"{b['sharpe']:>17.2f}"
        )

        a_value = f"${a['ending_value']:,.2f}"
        b_value = f"${b['ending_value']:,.2f}"

        builder.line(f"{'Growth of $10,000':<25}" f"{a_value:>17}" f"{b_value:>17}")

        builder.blank()

        builder.section(f"Portfolio A: {portfolio_a.name}")

        for holding in portfolio_a.holdings:
            builder.field(holding.fund.symbol, f"{holding.allocation:.1f}%")

        builder.blank()

        builder.section(f"Portfolio B: {portfolio_b.name}")

        for holding in portfolio_b.holdings:
            builder.field(holding.fund.symbol, f"{holding.allocation:.1f}%")

        builder.save(filename)
        return filename
