"""Menu-driven console entry point for the Investment Analyzer."""

from investment_analyzer.analysis.cycle_analyzer import MarketCycleAnalyzer
from investment_analyzer.core.file_discovery import discover_funds
from investment_analyzer.models.fund import Fund
from investment_analyzer.reports.excel_report import ExcelReport
from investment_analyzer.analysis.portfolio_comparator import PortfolioComparator
from charts import growth_chart
from loader import load_fund
from ranking import (
    print_executive_summary,
    print_rankings,
    print_recommendation,
)
from investment_analyzer.models.portfolio import Portfolio
from investment_analyzer.analysis.portfolio_analyzer import PortfolioAnalyzer
from investment_analyzer.reports.report_manager import ReportManager

from report import save_report
from returns import monthly_returns
from statistics import (
    best_year,
    cagr,
    fund_statistics,
    max_drawdown,
    negative_years,
    positive_years,
    worst_year,
)


def display_menu():
    """Display the available actions and return a valid selection."""
    while True:
        print()
        print("Menu")
        print("-" * 50)
        print("1. Analyze all funds")
        print("2. Generate Excel market-cycle report")
        print("3. Analyze one fund")
        print("4. Compare selected funds")
        print("5. Analyze a portfolio")
        print("6. Compare two portfolios")
        print("7. Exit")
        print()

        choice = input("Selection: ").strip()

        if choice in {"1", "2", "3", "4", "5", "6", "7"}:
            return choice

        print()
        print("Invalid selection. Please enter a number from 1 to 7.")
        choice = input("Selection: ").strip()

        if choice in {"1", "2", "3", "4", "5"}:
            return choice

        print("\nInvalid selection. Please enter a number from 1 to 5.\n")


def select_fund(funds):
    """Let the user select one discovered fund, or return to the menu."""
    print("\nChoose a fund to analyze:\n")

    for number, symbol in enumerate(funds, start=1):
        print(f"{number}. {symbol}")

    print("B. Back to menu\n")

    while True:
        selection = input("Selection: ").strip()

        if selection.lower() == "b":
            return None

        if selection.isdigit():
            index = int(selection) - 1
            if 0 <= index < len(funds):
                return funds[index]

        print("\nPlease enter a fund number or B to return to the menu.\n")


def select_funds_for_comparison(funds):
    """Return two or more selected funds, or None to return to the menu."""
    print("\nChoose two or more funds to compare:\n")

    for number, symbol in enumerate(funds, start=1):
        print(f"{number}. {symbol}")

    print("B. Back to menu\n")
    print("Enter numbers separated by commas, such as: 1,3,6\n")

    while True:
        selection = input("Selection: ").strip()

        if selection.lower() == "b":
            return None

        try:
            numbers = [int(value.strip()) for value in selection.split(",")]
        except ValueError:
            numbers = []

        selected_funds = []
        for number in numbers:
            index = number - 1
            if 0 <= index < len(funds) and funds[index] not in selected_funds:
                selected_funds.append(funds[index])

        if len(selected_funds) >= 2 and len(selected_funds) == len(numbers):
            return selected_funds

        print(
            "\nPlease enter at least two valid, different fund numbers "
            "separated by commas.\n"
        )


def analyze_funds(funds):
    """Run the existing performance analysis for every discovered fund."""
    fund_returns = {}
    results = {}

    print("\nAnalyzing funds...\n")

    for symbol in funds:
        df = load_fund(symbol)
        returns = monthly_returns(df)
        statistics = fund_statistics(returns)

        fund_returns[symbol] = returns
        results[symbol] = {
            "CAGR": cagr(df),
            "Return": statistics["Annualized Return"],
            "Volatility": statistics["Annualized Volatility"],
            "Drawdown": max_drawdown(df),
            "Best Year": best_year(df),
            "Worst Year": worst_year(df),
            "Positive Years": positive_years(df),
            "Negative Years": negative_years(df),
        }

        print(symbol)
        print("-" * 40)
        print(f"CAGR                  : {results[symbol]['CAGR']:.2%}")
        print(f"Annualized Return     : {results[symbol]['Return']:.2%}")
        print(f"Annualized Volatility : {results[symbol]['Volatility']:.2%}")
        print(f"Maximum Drawdown      : {results[symbol]['Drawdown']:.2%}")
        print(f"Best Year             : {results[symbol]['Best Year']:.2%}")
        print(f"Worst Year            : {results[symbol]['Worst Year']:.2%}")
        print(f"Positive Years        : {results[symbol]['Positive Years']}")
        print(f"Negative Years        : {results[symbol]['Negative Years']}")
        print()

    print("=" * 80)
    print("FUND COMPARISON")
    print("=" * 80)
    print(
        f"{'Fund':<8}"
        f"{'CAGR':>10}"
        f"{'Return':>10}"
        f"{'Vol':>10}"
        f"{'Max DD':>10}"
        f"{'Best':>10}"
        f"{'Worst':>10}"
    )
    print("-" * 68)

    for symbol, data in results.items():
        print(
            f"{symbol:<8}"
            f"{data['CAGR']:>10.2%}"
            f"{data['Return']:>10.2%}"
            f"{data['Volatility']:>10.2%}"
            f"{data['Drawdown']:>10.2%}"
            f"{data['Best Year']:>10.2%}"
            f"{data['Worst Year']:>10.2%}"
        )

    growth_chart(fund_returns)
    save_report(results)
    print_rankings(results)
    print_executive_summary(results)
    print_recommendation(results)


def generate_excel_report(funds):
    """Generate the market-cycle workbook for every discovered fund."""
    report = ExcelReport()

    print("\nCreating Excel market-cycle report...\n")

    for symbol in funds:
        print(f"Processing {symbol}...")
        fund = Fund(symbol).load_data()
        cycles = MarketCycleAnalyzer(fund).build_cycles()
        report.add_fund(symbol, cycles)

    output_file = report.save()
    print(f"\nWorkbook written to:\n{output_file}\n")


def create_portfolio(funds):
    """
    Interactively create a portfolio from the available funds.

    Returns None if the user cancels.
    """

    print()
    print("Create Portfolio")
    print("-" * 50)

    name = input("Portfolio name (or B to return to menu): ").strip()

    if name.lower() == "b":
        return None

    if not name:
        name = "Portfolio"

    portfolio = Portfolio(name)

    print()
    print("Available funds:")
    print()

    for number, symbol in enumerate(funds, start=1):
        print(f"{number}. {symbol}")

    print()
    print("Enter fund numbers and allocations.")
    print("Allocations must total 100%.")
    print("Enter B at a fund prompt to cancel.")
    print()

    while portfolio.total_allocation < 100.0:
        remaining = 100.0 - portfolio.total_allocation

        print(f"Remaining allocation: {remaining:.1f}%")

        selection = input("Fund number (or B): ").strip()

        if selection.lower() == "b":
            print()
            print("Portfolio creation cancelled.")
            return None

        if not selection.isdigit():
            print("Please enter a valid fund number or B.")
            print()
            continue

        index = int(selection) - 1

        if index < 0 or index >= len(funds):
            print("Please enter a valid fund number.")
            print()
            continue

        symbol = funds[index]

        if any(holding.fund.symbol == symbol for holding in portfolio.holdings):
            print(f"{symbol} is already in the portfolio.")
            print()
            continue

        allocation_text = input("Allocation % (or B): ").strip()

        if allocation_text.lower() == "b":
            print()
            print("Portfolio creation cancelled.")
            return None

        try:
            allocation = float(allocation_text)
        except ValueError:
            print("Please enter a valid allocation.")
            print()
            continue

        if allocation <= 0:
            print("Allocation must be greater than zero.")
            print()
            continue

        if allocation > remaining:
            print(f"Allocation cannot exceed the remaining " f"{remaining:.1f}%.")
            print()
            continue

        portfolio.add_fund(symbol, allocation)

        print(f"Added {symbol}: {allocation:.1f}%")
        print()

    portfolio.validate()

    print("Portfolio complete.")
    portfolio.summary()

    confirm = input("\nAnalyze this portfolio? (Y/N): ").strip().lower()

    if confirm != "y":
        print()
        print("Portfolio analysis cancelled.")
        return None

    return portfolio


def analyze_portfolio_interactive(funds):
    """
    Create, analyze, and report an interactive portfolio.
    """

    portfolio = create_portfolio(funds)

    if portfolio is None:
        return

    analyzer = PortfolioAnalyzer(portfolio)
    print("PORTFOLIO PERFORMANCE STATISTICS")
    print("=" * 60)

    print(f"CAGR                  : " f"{analyzer.cagr():.2%}")

    print(f"Annualized Avg Return : " f"{analyzer.annualized_return():.2%}")

    print(f"Annualized Volatility : " f"{analyzer.annualized_volatility():.2%}")

    print(f"Maximum Drawdown      : " f"{analyzer.max_drawdown():.2%}")

    print(f"Sharpe Ratio          : " f"{analyzer.sharpe_ratio():.2f}")

    growth = analyzer.growth_index(10000)

    print()
    print("Growth of $10,000")
    print("-" * 60)

    print("Beginning Value : $10,000.00")
    print(f"Ending Value    : " f"${growth.iloc[-1]:,.2f}")

    manager = ReportManager()

    filename = manager.create_portfolio_report(portfolio)

    print()
    print("Portfolio report created:")
    print(filename)


def compare_portfolios_interactive(funds):
    """
    Interactively create and compare two portfolios.
    """

    print()
    print("=" * 60)
    print("CREATE PORTFOLIO A")
    print("=" * 60)

    portfolio_a = create_portfolio(funds)

    if portfolio_a is None:
        return

    print()
    print("=" * 60)
    print("CREATE PORTFOLIO B")
    print("=" * 60)

    portfolio_b = create_portfolio(funds)

    if portfolio_b is None:
        print()
        print("Portfolio comparison cancelled.")
        return

    comparator = PortfolioComparator(
        portfolio_a,
        portfolio_b,
    )

    results = comparator.compare()

    a = results["portfolio_a"]
    b = results["portfolio_b"]

    print()
    print("PORTFOLIO COMPARISON")
    print("=" * 78)

    print(f"{'Metric':<25}" f"{'Portfolio A':>20}" f"{'Portfolio B':>20}")

    print("-" * 78)

    print(f"{'CAGR':<25}" f"{a['cagr']:>19.2%}" f"{b['cagr']:>20.2%}")

    print(
        f"{'Annualized Avg Return':<25}"
        f"{a['annualized_return']:>19.2%}"
        f"{b['annualized_return']:>20.2%}"
    )

    print(
        f"{'Annualized Volatility':<25}"
        f"{a['volatility']:>19.2%}"
        f"{b['volatility']:>20.2%}"
    )

    print(
        f"{'Maximum Drawdown':<25}"
        f"{a['max_drawdown']:>19.2%}"
        f"{b['max_drawdown']:>20.2%}"
    )

    print(f"{'Sharpe Ratio':<25}" f"{a['sharpe']:>19.2f}" f"{b['sharpe']:>20.2f}")

    a_value = f"${a['ending_value']:,.2f}"
    b_value = f"${b['ending_value']:,.2f}"

    print(f"{'Growth of $10,000':<25}" f"{a_value:>20}" f"{b_value:>20}")

    interpretation = comparator.interpretation()

    print()
    print("COMPARISON INTERPRETATION")
    print("=" * 60)

    print()
    print("Growth:")
    print(interpretation["growth"])

    print()
    print("Risk:")
    print(interpretation["risk"])

    print()
    print("Drawdown:")
    print(interpretation["drawdown"])

    print()
    print("Risk-Adjusted Performance:")
    print(interpretation["risk_adjusted"])

    print()
    print("Growth of $10,000:")
    print(interpretation["ending_value"])

    manager = ReportManager()

    filename = manager.create_comparison_report(
        portfolio_a,
        portfolio_b,
    )

    print()
    print("Portfolio comparison report created:")
    print(filename)


def main():
    """Discover funds, present the menu, and run the chosen action."""
    funds = discover_funds()

    print()
    print("=" * 60)
    print("Investment Analyzer")
    print("=" * 60)

    if not funds:
        print("\nNo CSV files were found in the data folder.")
        return

    print(f"\nFound {len(funds)} fund(s):\n")
    for fund in funds:
        print(f"  {fund}")
    print()

    while True:
        choice = display_menu()

        if choice == "1":
            analyze_funds(funds)
        elif choice == "2":
            generate_excel_report(funds)
        elif choice == "3":
            selected_fund = select_fund(funds)
            if selected_fund:
                analyze_funds([selected_fund])
        elif choice == "4":
            selected_funds = select_funds_for_comparison(funds)
            if selected_funds:
                print(f"\nComparing: {', '.join(selected_funds)}")
                analyze_funds(selected_funds)

        elif choice == "5":
            analyze_portfolio_interactive(funds)
        elif choice == "6":
            compare_portfolios_interactive(funds)
        else:
            print()
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()
