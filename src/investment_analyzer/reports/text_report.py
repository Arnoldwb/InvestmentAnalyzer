from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.analysis.portfolio_comparator import PortfolioComparator
from investment_analyzer.analysis.monte_carlo_analyzer import MonteCarloAnalyzer
from investment_analyzer.analysis.scenario_analyzer import ScenarioAnalyzer
from investment_analyzer.analysis.historical_scenarios import HISTORICAL_SCENARIOS
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
            "Investment Analyzer\n" "Version 5.3\n" "Portfolio Analysis Report"
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
        builder.section("Major Historical Drawdowns")

        major_drawdowns = analyzer.major_drawdowns(threshold=0.10)

        builder.line(
            f"{'Peak':<11}"
            f"{'Bottom':<11}"
            f"{'Recovery':<11}"
            f"{'Decline':>9}"
            f"{'To Bottom':>11}"
            f"{'Recover':>10}"
            f"{'Total':>9}"
        )

        builder.line("-" * 72)

        for episode in major_drawdowns:
            peak = episode["peak_date"].strftime("%Y-%m")
            bottom = episode["bottom_date"].strftime("%Y-%m")
            recovery = episode["recovery_date"].strftime("%Y-%m")

            builder.line(
                f"{peak:<11}"
                f"{bottom:<11}"
                f"{recovery:<11}"
                f"{episode['decline']:>9.2%}"
                f"{episode['days_to_bottom']:>11}"
                f"{episode['days_bottom_to_recovery']:>10}"
                f"{episode['days_to_recovery']:>9}"
            )

        builder.blank()
        builder.section("Historical Stress Interpretation")

        stress = analyzer.stress_interpretation(threshold=0.10)

        for text in stress.values():
            builder.line(text)
            builder.blank()
        builder.section("Historical Scenario Comparison")

        scenario_analyzer = ScenarioAnalyzer(portfolio)

        builder.line(
            f"{'Scenario':<27}"
            f"{'Return':>10}"
            f"{'Drawdown':>11}"
            f"{'Peak Recovery':>15}"
        )

        builder.line("-" * 60)

        for scenario in HISTORICAL_SCENARIOS.values():
            try:
                scenario_result = scenario_analyzer.analyze_scenario(
                    scenario
                )

                recovery = scenario_analyzer.recovery_analysis(
                    scenario["start_date"],
                    scenario["end_date"],
                )

            except ValueError:
                builder.line(
                    f"{scenario['name']:<27}"
                    f"{'N/A':>10}"
                    f"{'N/A':>11}"
                    f"{'No data':>15}"
                )
                continue

            recovery_days = recovery["days_to_recovery"]

            recovery_text = (
                f"{recovery_days:,} days"
                if recovery_days is not None
                else "N/A"
            )

            builder.line(
                f"{scenario['name']:<27}"
                f"{scenario_result['total_return']:>10.2%}"
                f"{scenario_result['max_drawdown']:>11.2%}"
                f"{recovery_text:>15}"
            )

        builder.blank()

        builder.section("Historical Stress Scenarios")

        for scenario in HISTORICAL_SCENARIOS.values():
            builder.line(scenario["name"])
            builder.line("-" * 40)

            try:
                scenario_result = scenario_analyzer.analyze_scenario(
                    scenario
                )

                recovery = scenario_analyzer.recovery_analysis(
                    scenario["start_date"],
                    scenario["end_date"],
                )

            except ValueError:
                builder.line(
                    "N/A — No portfolio return data exists "
                    "for this scenario period."
                )
                builder.blank()
                continue

            builder.field(
                "Scenario Return",
                f"{scenario_result['total_return']:.2%}",
            )

            builder.field(
                "Maximum Drawdown",
                f"{scenario_result['max_drawdown']:.2%}",
            )

            builder.field(
                "Peak",
                recovery["peak_date"].strftime("%b %Y"),
            )

            builder.field(
                "Bottom",
                recovery["bottom_date"].strftime("%b %Y"),
            )

            if recovery["recovery_date"] is not None:
                builder.field(
                    "Full Recovery",
                    recovery["recovery_date"].strftime("%b %Y"),
                )

                builder.field(
                    "Peak to Bottom",
                    f"{recovery['days_to_bottom']:,} days",
                )

                builder.field(
                    "Bottom to Recovery",
                    f"{recovery['days_bottom_to_recovery']:,} days",
                )

                builder.field(
                    "Peak to Recovery",
                    f"{recovery['days_to_recovery']:,} days",
                )
            else:
                builder.field(
                    "Full Recovery",
                    "Not reached in available data",
                )

            builder.blank()

            builder.line("Interpretation:")
            builder.line(
                scenario_analyzer.interpretation(scenario)
            )

            builder.blank()

        try:
            portfolio.validate()
            builder.field("Portfolio Validation", "PASSED")
        except ValueError:
            builder.field("Portfolio Validation", "FAILED")

        builder.save(filename)

        return filename

    def create_monte_carlo_report(
        self,
        portfolio,
        initial_value,
        years,
        simulations=10000,
        target_value=None,
        seed=None,
        summary=None,
    ):
        """
        Create a Monte Carlo portfolio analysis report.
        """

        filename = self.report_path("MonteCarloReport.txt")

        if summary is None:
            analyzer = MonteCarloAnalyzer(portfolio)

            summary = analyzer.summary(
                initial_value=initial_value,
                years=years,
                simulations=simulations,
                seed=seed,
                target_value=target_value,
            )

        builder = ReportBuilder()

        builder.title(
            "Investment Analyzer\n"
            "Version 5.3\n"
            "Monte Carlo Portfolio Analysis Report"
        )

        builder.field("Generated:", self.timestamp)
        builder.blank()

        builder.field("Portfolio", portfolio.name)
        builder.field(
            "Starting Value",
            f"${initial_value:,.2f}",
        )
        builder.field(
            "Projection Period",
            f"{years} years",
        )
        builder.field(
            "Simulations",
            f"{simulations:,}",
        )

        if target_value is not None:
            builder.field(
                "Target Value",
                f"${target_value:,.2f}",
            )

        builder.blank()
        builder.section("Portfolio Holdings")

        for holding in portfolio.holdings:
            builder.field(
                holding.fund.symbol,
                f"{holding.allocation:.1f}%",
            )

        builder.line("-" * 60)
        builder.field(
            "Total Allocation",
            f"{portfolio.total_allocation:.1f}%",
        )

        builder.blank()
        builder.section("Projected Ending Values")

        builder.field(
            "10th Percentile",
            f"${summary['percentile_10']:,.2f}",
        )
        builder.field(
            "25th Percentile",
            f"${summary['percentile_25']:,.2f}",
        )
        builder.field(
            "Median",
            f"${summary['median']:,.2f}",
        )
        builder.field(
            "75th Percentile",
            f"${summary['percentile_75']:,.2f}",
        )
        builder.field(
            "90th Percentile",
            f"${summary['percentile_90']:,.2f}",
        )
        builder.field(
            "Mean Ending Value",
            f"${summary['mean_ending_value']:,.2f}",
        )

        builder.blank()
        builder.section("Probability Analysis")

        builder.field(
            "Above Starting Value",
            f"{summary['probability_above_start']:.2%}",
        )

        if target_value is not None:
            builder.field(
                "At or Above Target",
                f"{summary['probability_above_target']:.2%}",
            )

        builder.blank()
        builder.section("Methodology")

        builder.line(
            "The simulation samples historical monthly portfolio "
            "returns with replacement."
        )
        builder.line(
            "Each simulated path compounds randomly sampled monthly "
            "returns over the projection period."
        )
        builder.blank()
        builder.line(
            "Monte Carlo results are simulations based on historical "
            "returns and are not forecasts or guarantees."
        )

        builder.save(filename)

        return filename

    def create_withdrawal_report(
        self,
        portfolio,
        initial_value,
        annual_withdrawal,
        years,
        simulations=10000,
        seed=None,
        summary=None,
        inflation_rate=0.0,
    ):
        """
        Create a Monte Carlo withdrawal sustainability report.
        """

        filename = self.report_path(
            "WithdrawalSustainabilityReport.txt"
        )

        if summary is None:
            analyzer = MonteCarloAnalyzer(portfolio)

            summary = analyzer.withdrawal_summary(
                initial_value=initial_value,
                annual_withdrawal=annual_withdrawal,
                years=years,
                simulations=simulations,
                seed=seed,
                inflation_rate=inflation_rate,
            )

        builder = ReportBuilder()

        builder.title(
            "Investment Analyzer\n"
            "Version 5.3\n"
            "Withdrawal Sustainability Analysis Report"
        )

        builder.field("Generated:", self.timestamp)
        builder.blank()

        builder.field("Portfolio", portfolio.name)
        builder.field(
            "Starting Value",
            f"${initial_value:,.2f}",
        )
        builder.field(
            "Annual Withdrawal",
            f"${annual_withdrawal:,.2f}",
        )
        builder.field(
            "Initial Withdrawal Rate",
            f"{summary['withdrawal_rate']:.2%}",
        )
        builder.field(
            "Annual Inflation Rate",
            f"{summary['inflation_rate']:.2%}",
        )
        builder.field(
            "Projection Period",
            f"{years} years",
        )
        builder.field(
            "Simulations",
            f"{simulations:,}",
        )

        builder.blank()
        builder.section("Portfolio Holdings")

        for holding in portfolio.holdings:
            builder.field(
                holding.fund.symbol,
                f"{holding.allocation:.1f}%",
            )

        builder.line("-" * 60)
        builder.field(
            "Total Allocation",
            f"{portfolio.total_allocation:.1f}%",
        )

        builder.blank()
        builder.section("Withdrawal Sustainability")

        builder.field(
            "Survival Probability",
            f"{summary['survival_probability']:.2%}",
        )
        builder.field(
            "Depletion Probability",
            f"{summary['depletion_probability']:.2%}",
        )

        builder.blank()
        builder.section("Projected Ending Values")

        builder.field(
            "10th Percentile",
            f"${summary['percentile_10']:,.2f}",
        )
        builder.field(
            "25th Percentile",
            f"${summary['percentile_25']:,.2f}",
        )
        builder.field(
            "Median",
            f"${summary['median']:,.2f}",
        )
        builder.field(
            "75th Percentile",
            f"${summary['percentile_75']:,.2f}",
        )
        builder.field(
            "90th Percentile",
            f"${summary['percentile_90']:,.2f}",
        )
        builder.field(
            "Mean Ending Value",
            f"${summary['mean_ending_value']:,.2f}",
        )

        builder.blank()
        builder.section("Methodology")

        builder.line(
            "The simulation samples historical monthly portfolio "
            "returns with replacement."
        )
        builder.line(
            "The annual withdrawal is divided into equal monthly "
            "withdrawals during each simulated path."
        )
        builder.line(
            "The annual withdrawal is increased once each year by "
            "the specified inflation rate."
        )
        builder.line(
            "Portfolio values are not allowed to fall below zero."
        )

        builder.blank()
        builder.line(
            "Monte Carlo results are simulations based on historical "
            "returns and are not forecasts or guarantees."
        )

        builder.save(filename)

        return filename
    def create_sustainable_withdrawal_report(
        self,
        portfolio,
        initial_value,
        years,
        target_survival_probability,
        simulations=10000,
        seed=None,
        inflation_rate=0.0,
        result=None,
    ):
        """
        Create a sustainable withdrawal analysis report.
        """

        filename = self.report_path(
            "SustainableWithdrawalReport.txt"
        )

        if result is None:
            analyzer = MonteCarloAnalyzer(portfolio)

            result = analyzer.sustainable_withdrawal(
                initial_value=initial_value,
                years=years,
                target_survival_probability=(
                    target_survival_probability
                ),
                simulations=simulations,
                seed=seed,
                inflation_rate=inflation_rate,
            )

        builder = ReportBuilder()

        builder.title(
            "Investment Analyzer\n"
            "Version 5.3\n"
            "Sustainable Withdrawal Analysis Report"
        )

        builder.field("Generated:", self.timestamp)
        builder.blank()

        builder.field("Portfolio", portfolio.name)
        builder.field(
            "Starting Value",
            f"${initial_value:,.2f}",
        )
        builder.field(
            "Projection Period",
            f"{years} years",
        )
        builder.field(
            "Annual Inflation Rate",
            f"{inflation_rate:.2%}",
        )
        builder.field(
            "Target Survival",
            f"{target_survival_probability:.2%}",
        )
        builder.field(
            "Simulations",
            f"{simulations:,}",
        )

        builder.blank()
        builder.section("Portfolio Holdings")

        for holding in portfolio.holdings:
            builder.field(
                holding.fund.symbol,
                f"{holding.allocation:.1f}%",
            )

        builder.line("-" * 60)
        builder.field(
            "Total Allocation",
            f"{portfolio.total_allocation:.1f}%",
        )

        builder.blank()
        builder.section("Sustainable Withdrawal Results")

        builder.field(
            "Sustainable Withdrawal",
            f"${result['annual_withdrawal']:,.2f}",
        )
        builder.field(
            "Initial Withdrawal Rate",
            f"{result['withdrawal_rate']:.2%}",
        )
        builder.field(
            "Actual Survival",
            f"{result['survival_probability']:.2%}",
        )

        builder.blank()
        builder.section("Methodology")

        builder.line(
            "The calculator searches for an initial annual withdrawal "
            "that meets the specified survival-probability target."
        )
        builder.line(
            "The simulation samples historical monthly portfolio "
            "returns with replacement."
        )
        builder.line(
            "The annual withdrawal is increased once each year by "
            "the specified inflation rate."
        )
        builder.line(
            "Portfolio values are not allowed to fall below zero."
        )

        builder.blank()
        builder.line(
            "The sustainable withdrawal is an estimate based on "
            "historical-return simulations and is not a guarantee."
        )

        builder.save(filename)

        return filename

    def create_withdrawal_strategy_comparison_report(
        self,
        portfolio,
        initial_value,
        annual_withdrawals,
        years,
        simulations=10000,
        seed=None,
        inflation_rate=0.0,
        results=None,
    ):
        """
        Create a Monte Carlo withdrawal strategy comparison report.
        """

        filename = self.report_path(
            "WithdrawalStrategyComparisonReport.txt"
        )

        if results is None:
            analyzer = MonteCarloAnalyzer(portfolio)

            results = analyzer.compare_withdrawal_strategies(
                initial_value=initial_value,
                annual_withdrawals=annual_withdrawals,
                years=years,
                simulations=simulations,
                seed=seed,
                inflation_rate=inflation_rate,
            )

        builder = ReportBuilder()

        builder.title(
            "Investment Analyzer\n"
            "Version 5.3\n"
            "Withdrawal Strategy Comparison Report"
        )

        builder.field("Generated:", self.timestamp)
        builder.blank()

        builder.field("Portfolio", portfolio.name)
        builder.field(
            "Starting Value",
            f"${initial_value:,.2f}",
        )
        builder.field(
            "Projection Period",
            f"{years} years",
        )
        builder.field(
            "Annual Inflation Rate",
            f"{inflation_rate:.2%}",
        )
        builder.field(
            "Simulations",
            f"{simulations:,}",
        )

        builder.blank()
        builder.section("Portfolio Holdings")

        for holding in portfolio.holdings:
            builder.field(
                holding.fund.symbol,
                f"{holding.allocation:.1f}%",
            )

        builder.line("-" * 60)
        builder.field(
            "Total Allocation",
            f"{portfolio.total_allocation:.1f}%",
        )

        builder.blank()
        builder.section("Withdrawal Strategy Comparison")

        builder.line(
            f"{'Withdrawal':>14} "
            f"{'Rate':>8} "
            f"{'Survival':>10} "
            f"{'Depletion':>10} "
            f"{'Median Ending':>18}"
        )
        builder.line("-" * 78)

        for result in results:
            builder.line(
                f"${result['annual_withdrawal']:>13,.2f} "
                f"{result['withdrawal_rate']:>7.2%} "
                f"{result['survival_probability']:>9.2%} "
                f"{result['depletion_probability']:>9.2%} "
                f"${result['median']:>17,.2f}"
            )

        builder.blank()
        builder.section("Interpretation")

        builder.line(
            "Higher withdrawals generally increase depletion risk "
            "and reduce projected ending values."
        )

        builder.blank()
        builder.section("Methodology")

        builder.line(
            "Each withdrawal strategy is tested using Monte Carlo "
            "simulation of historical monthly portfolio returns."
        )
        builder.line(
            "The annual withdrawal is divided into equal monthly "
            "withdrawals during each simulated path."
        )
        builder.line(
            "The annual withdrawal is increased once each year by "
            "the specified inflation rate."
        )
        builder.line(
            "Portfolio values are not allowed to fall below zero."
        )

        builder.blank()
        builder.line(
            "Monte Carlo results are simulations based on historical "
            "returns and are not forecasts or guarantees."
        )

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
            "Investment Analyzer\n" "Version 5.3\n" "Portfolio Comparison Report"
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

        builder.blank()

        builder.section("Comparison Interpretation")

        interpretation = comparator.interpretation()

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

        builder.line("Growth of $10,000:")
        builder.line(interpretation["ending_value"])

        builder.save(filename)

        return filename
