"""Menu-driven console entry point for the Investment Analyzer."""

from investment_analyzer.analysis.cycle_analyzer import MarketCycleAnalyzer
from investment_analyzer.core.file_discovery import discover_funds
from investment_analyzer.core.portfolio_storage import (
    delete_portfolio,
    list_portfolios,
    load_portfolio,
    rename_portfolio,
    save_portfolio,
)
from investment_analyzer.models.fund import Fund
from investment_analyzer.reports.excel_report import ExcelReport
from investment_analyzer.analysis.portfolio_comparator import PortfolioComparator
from investment_analyzer.analysis.rebalancing_analyzer import RebalancingAnalyzer
from investment_analyzer.analysis.monte_carlo_analyzer import MonteCarloAnalyzer
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
        print("7. Manage saved portfolios")
        print("8. Rebalance a saved portfolio")
        print("9. Monte Carlo portfolio analysis")
        print("10. Exit")
        print()

        choice = input("Selection: ").strip()

        if choice in {
            "1", "2", "3", "4", "5",
            "6", "7", "8", "9", "10"
        }:
            return choice

        print()
        print("Invalid selection. Please enter a number from 1 to 10.")


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


def create_portfolio(funds, confirm_analysis=True):
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

    if confirm_analysis:
        confirm = input(
            "\nAnalyze this portfolio? (Y/N): "
        ).strip().lower()

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

    save_choice = input("\nSave this portfolio? (Y/N): ").strip().lower()

    if save_choice == "y":
        saved_path = save_portfolio(portfolio)
        print()
        print("Portfolio saved:")
        print(saved_path)


def display_portfolio_comparison(portfolio_a, portfolio_b):
    """
    Display, interpret, and report a comparison of two portfolios.
    """
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
    print(f"Portfolio A: {portfolio_a.name}")
    print(f"Portfolio B: {portfolio_b.name}")
    print()

    print(
        f"{'Metric':<25}"
        f"{'Portfolio A':>20}"
        f"{'Portfolio B':>20}"
    )

    print("-" * 78)

    print(
        f"{'CAGR':<25}"
        f"{a['cagr']:>19.2%}"
        f"{b['cagr']:>20.2%}"
    )

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

    print(
        f"{'Sharpe Ratio':<25}"
        f"{a['sharpe']:>19.2f}"
        f"{b['sharpe']:>20.2f}"
    )

    a_value = f"${a['ending_value']:,.2f}"
    b_value = f"${b['ending_value']:,.2f}"

    print(
        f"{'Growth of $10,000':<25}"
        f"{a_value:>20}"
        f"{b_value:>20}"
    )

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

    display_portfolio_comparison(
        portfolio_a,
        portfolio_b,
    )





def display_rebalancing_changes(current, proposed):
    """
    Display the allocation changes required to move from the
    current portfolio to the proposed portfolio.
    """
    analyzer = RebalancingAnalyzer(current, proposed)
    changes = analyzer.allocation_changes()

    print()
    print("REBALANCING CHANGES")
    print("=" * 60)

    print(
        f"{'Fund':<10}"
        f"{'Current':>12}"
        f"{'Proposed':>12}"
        f"{'Change':>12}"
    )

    print("-" * 60)

    for item in changes:
        print(
            f"{item['symbol']:<10}"
            f"{item['current']:>11.1f}%"
            f"{item['proposed']:>11.1f}%"
            f"{item['change']:>+11.1f}%"
        )

    print("-" * 60)

    total_current = sum(item["current"] for item in changes)
    total_proposed = sum(item["proposed"] for item in changes)
    total_change = sum(item["change"] for item in changes)

    print(
        f"{'Total':<10}"
        f"{total_current:>11.1f}%"
        f"{total_proposed:>11.1f}%"
        f"{total_change:>+11.1f}%"
    )



def display_dollar_rebalancing(current, proposed, portfolio_value):
    """
    Display the dollar amounts required to rebalance a portfolio.
    """
    analyzer = RebalancingAnalyzer(current, proposed)
    changes = analyzer.dollar_changes(portfolio_value)

    print()
    print("DOLLAR REBALANCING")
    print("=" * 78)

    print(
        f"{'Fund':<10}"
        f"{'Current Value':>18}"
        f"{'Proposed Value':>18}"
        f"{'Buy / Sell':>18}"
    )

    print("-" * 78)

    for item in changes:
        current_value = f"${item['current_value']:,.2f}"
        proposed_value = f"${item['proposed_value']:,.2f}"

        change = item["dollar_change"]

        if change > 0:
            change_text = f"+${change:,.2f}"
        elif change < 0:
            change_text = f"-${abs(change):,.2f}"
        else:
            change_text = "$0.00"

        print(
            f"{item['symbol']:<10}"
            f"{current_value:>18}"
            f"{proposed_value:>18}"
            f"{change_text:>18}"
        )

    print("-" * 78)

    total_current = sum(
        item["current_value"] for item in changes
    )
    total_proposed = sum(
        item["proposed_value"] for item in changes
    )
    total_change = sum(
        item["dollar_change"] for item in changes
    )

    total_current_text = f"${total_current:,.2f}"
    total_proposed_text = f"${total_proposed:,.2f}"
    total_change_text = f"${total_change:,.2f}"

    print(
        f"{'Total':<10}"
        f"{total_current_text:>18}"
        f"{total_proposed_text:>18}"
        f"{total_change_text:>18}"
    )

    total_sales = sum(
        -item["dollar_change"]
        for item in changes
        if item["dollar_change"] < 0
    )

    total_purchases = sum(
        item["dollar_change"]
        for item in changes
        if item["dollar_change"] > 0
    )

    print()
    print(f"Total to sell: ${total_sales:,.2f}")
    print(f"Total to buy : ${total_purchases:,.2f}")


def rebalance_saved_portfolio_interactive(funds):
    """
    Compare a saved portfolio with a proposed new allocation.

    The original saved portfolio is never modified.
    """
    saved = list_portfolios()

    if not saved:
        print()
        print("No saved portfolios were found.")
        return

    print()
    print("=" * 60)
    print("PORTFOLIO REBALANCING ANALYSIS")
    print("=" * 60)

    print()
    print("Choose the current saved portfolio:")
    print()

    for number, filename in enumerate(saved, start=1):
        print(f"{number}. {filename}")

    print("B. Back to menu")
    print()

    while True:
        selection = input("Selection: ").strip()

        if selection.lower() == "b":
            return

        if selection.isdigit():
            index = int(selection) - 1

            if 0 <= index < len(saved):
                break

        print()
        print("Please enter a valid portfolio number or B.")

    current = load_portfolio(saved[index])

    print()
    print("CURRENT PORTFOLIO")
    print("=" * 60)
    current.summary()

    print()
    print("Now create the proposed rebalanced allocation.")
    print("The current saved portfolio will not be changed.")

    proposed = create_portfolio(funds, confirm_analysis=False)

    if proposed is None:
        print()
        print("Rebalancing analysis cancelled.")
        return

    current.name = f"{current.name} - Current"
    proposed.name = f"{proposed.name} - Proposed"

    display_rebalancing_changes(
        current,
        proposed,
    )

    print()
    value_text = input(
        "Enter total portfolio value for dollar rebalancing "
        "(or press Enter to skip): "
    ).strip()

    if value_text:
        try:
            portfolio_value = float(
                value_text.replace(",", "").replace("$", "")
            )

            display_dollar_rebalancing(
                current,
                proposed,
                portfolio_value,
            )
        except ValueError as error:
            print()
            print(f"Dollar rebalancing skipped: {error}")

    display_portfolio_comparison(
        current,
        proposed,
    )

    print()
    save_choice = input(
        "Save the proposed portfolio as a new saved portfolio? (Y/N): "
    ).strip().lower()

    if save_choice != "y":
        print()
        print("Proposed portfolio was not saved.")
        return

    proposed.name = proposed.name.removesuffix(" - Proposed")

    try:
        saved_path = save_portfolio(proposed)
    except FileExistsError as error:
        print()
        print(f"Unable to save proposed portfolio: {error}")
        return

    print()
    print("Proposed portfolio saved:")
    print(saved_path)


def edit_saved_portfolio_interactive(filename, funds):
    """
    Edit the holdings and allocations of a saved portfolio.
    """
    portfolio = load_portfolio(filename)

    while True:
        print()
        print("=" * 60)
        print("EDIT SAVED PORTFOLIO")
        print("=" * 60)

        portfolio.summary()

        print()
        print("A. Add a fund")
        print("C. Change an allocation")
        print("R. Remove a fund")
        print("S. Save changes")
        print("B. Cancel and return")
        print()

        action = input("Selection: ").strip().lower()

        if action == "b":
            print()
            print("Changes cancelled. Saved portfolio was not modified.")
            return

        if action == "a":
            available = [
                symbol
                for symbol in funds
                if all(
                    holding.fund.symbol != symbol
                    for holding in portfolio.holdings
                )
            ]

            if not available:
                print()
                print("All available funds are already in this portfolio.")
                continue

            print()
            print("Available Funds")
            print("-" * 40)

            for number, symbol in enumerate(available, start=1):
                print(f"{number}. {symbol}")

            selection = input("\nFund number: ").strip()

            if not selection.isdigit():
                print()
                print("Please enter a valid fund number.")
                continue

            index = int(selection) - 1

            if not 0 <= index < len(available):
                print()
                print("Please enter a valid fund number.")
                continue

            try:
                allocation = float(
                    input("Allocation percentage: ").strip()
                )
                portfolio.add_fund(available[index], allocation)
            except ValueError as error:
                print()
                print(f"Unable to add fund: {error}")
                continue

            print()
            print(f"{available[index]} added.")
            continue

        if action == "c":
            if not portfolio.holdings:
                print()
                print("This portfolio has no holdings.")
                continue

            print()
            for number, holding in enumerate(portfolio.holdings, start=1):
                print(
                    f"{number}. "
                    f"{holding.fund.symbol} "
                    f"{holding.allocation:.1f}%"
                )

            selection = input("\nHolding number: ").strip()

            if not selection.isdigit():
                print()
                print("Please enter a valid holding number.")
                continue

            index = int(selection) - 1

            if not 0 <= index < len(portfolio.holdings):
                print()
                print("Please enter a valid holding number.")
                continue

            symbol = portfolio.holdings[index].fund.symbol

            try:
                allocation = float(
                    input("New allocation percentage: ").strip()
                )
                portfolio.update_allocation(symbol, allocation)
            except ValueError as error:
                print()
                print(f"Unable to change allocation: {error}")
                continue

            print()
            print(f"{symbol} allocation updated.")
            continue

        if action == "r":
            if len(portfolio.holdings) <= 1:
                print()
                print("A portfolio must contain at least one fund.")
                continue

            print()
            for number, holding in enumerate(portfolio.holdings, start=1):
                print(
                    f"{number}. "
                    f"{holding.fund.symbol} "
                    f"{holding.allocation:.1f}%"
                )

            selection = input("\nHolding number to remove: ").strip()

            if not selection.isdigit():
                print()
                print("Please enter a valid holding number.")
                continue

            index = int(selection) - 1

            if not 0 <= index < len(portfolio.holdings):
                print()
                print("Please enter a valid holding number.")
                continue

            symbol = portfolio.holdings[index].fund.symbol
            portfolio.remove_fund(symbol)

            print()
            print(f"{symbol} removed.")
            continue

        if action == "s":
            try:
                portfolio.validate()
            except ValueError as error:
                print()
                print("Portfolio cannot be saved yet.")
                print(error)
                continue

            save_portfolio(portfolio, filename)

            print()
            print("Portfolio changes saved:")
            print(filename)
            return

        print()
        print("Please enter A, C, R, S, or B.")


def manage_saved_portfolios_interactive(funds):
    """
    Manage previously saved portfolios.
    """
    while True:
        saved = list_portfolios()

        print()
        print("=" * 60)
        print("MANAGE SAVED PORTFOLIOS")
        print("=" * 60)

        if not saved:
            print()
            print("No saved portfolios were found.")
            return

        print()
        for number, filename in enumerate(saved, start=1):
            print(f"{number}. {filename}")

        print()
        print("O. Open and analyze a portfolio")
        print("E. Edit a portfolio")
        print("R. Rename a portfolio")
        print("D. Delete a portfolio")
        print("B. Back to main menu")
        print()

        action = input("Selection: ").strip().lower()

        if action == "b":
            return

        if action == "o":
            open_saved_portfolio_interactive()
            continue

        if action not in {"e", "r", "d"}:
            print()
            print("Please enter O, E, R, D, or B.")
            continue

        selection = input("Portfolio number: ").strip()

        if not selection.isdigit():
            print()
            print("Please enter a valid portfolio number.")
            continue

        index = int(selection) - 1

        if not 0 <= index < len(saved):
            print()
            print("Please enter a valid portfolio number.")
            continue

        filename = saved[index]

        if action == "e":
            edit_saved_portfolio_interactive(filename, funds)
            continue

        if action == "r":
            new_name = input("New portfolio name: ").strip()

            if not new_name:
                print()
                print("Portfolio name cannot be empty.")
                continue

            try:
                new_path = rename_portfolio(filename, new_name)
            except (ValueError, FileExistsError, FileNotFoundError) as error:
                print()
                print(f"Unable to rename portfolio: {error}")
                continue

            print()
            print("Portfolio renamed:")
            print(new_path.name)
            continue

        portfolio = load_portfolio(filename)

        print()
        print("Portfolio selected:")
        portfolio.summary()

        confirm = input(
            "\nDelete this portfolio permanently? (Y/N): "
        ).strip().lower()

        if confirm != "y":
            print()
            print("Delete cancelled.")
            continue

        try:
            deleted_path = delete_portfolio(filename)
        except FileNotFoundError as error:
            print()
            print(f"Unable to delete portfolio: {error}")
            continue

        print()
        print("Portfolio deleted:")
        print(deleted_path.name)


def open_saved_portfolio_interactive():
    """
    Select, load, and analyze a previously saved portfolio.
    """
    saved = list_portfolios()

    if not saved:
        print()
        print("No saved portfolios were found.")
        return

    print()
    print("Saved Portfolios")
    print("-" * 50)

    for number, filename in enumerate(saved, start=1):
        print(f"{number}. {filename}")

    print("B. Back to menu")
    print()

    while True:
        selection = input("Selection: ").strip()

        if selection.lower() == "b":
            return

        if selection.isdigit():
            index = int(selection) - 1

            if 0 <= index < len(saved):
                portfolio = load_portfolio(saved[index])

                print()
                print("Portfolio loaded:")
                portfolio.summary()

                analyze_loaded_portfolio(portfolio)
                return

        print("Please enter a valid portfolio number or B.")



def monte_carlo_saved_portfolio_interactive():
    """
    Run Monte Carlo analysis for a saved portfolio.
    """
    saved = list_portfolios()

    if not saved:
        print()
        print("No saved portfolios were found.")
        return

    print()
    print("=" * 60)
    print("MONTE CARLO PORTFOLIO ANALYSIS")
    print("=" * 60)

    print()
    print("Choose a saved portfolio:")
    print()

    for number, filename in enumerate(saved, start=1):
        print(f"{number}. {filename}")

    print("B. Back to menu")
    print()

    while True:
        selection = input("Selection: ").strip()

        if selection.lower() == "b":
            return

        if selection.isdigit():
            index = int(selection) - 1

            if 0 <= index < len(saved):
                break

        print()
        print("Please enter a valid portfolio number or B.")

    portfolio = load_portfolio(saved[index])

    print()
    print("SELECTED PORTFOLIO")
    print("=" * 60)
    portfolio.summary()

    while True:
        value_text = input(
            "\nStarting portfolio value (or B to cancel): $"
        ).strip()

        if value_text.lower() == "b":
            return

        try:
            initial_value = float(
                value_text.replace(",", "").replace("$", "")
            )

            if initial_value <= 0:
                raise ValueError

            break
        except ValueError:
            print()
            print("Please enter a portfolio value greater than zero.")

    while True:
        years_text = input(
            "Projection period in years (or B to cancel): "
        ).strip()

        if years_text.lower() == "b":
            return

        try:
            years = int(years_text)

            if years <= 0:
                raise ValueError

            break
        except ValueError:
            print()
            print("Please enter a whole number of years greater than zero.")

    while True:
        simulations_text = input(
            "Number of simulations "
            "(press Enter for 10,000): "
        ).strip()

        if not simulations_text:
            simulations = 10000
            break

        try:
            simulations = int(simulations_text)

            if simulations <= 0:
                raise ValueError

            break
        except ValueError:
            print()
            print(
                "Please enter a whole number of simulations "
                "greater than zero."
            )

    while True:
        target_text = input(
            "Target portfolio value "
            "(press Enter for none): $"
        ).strip()

        if not target_text:
            target_value = None
            break

        try:
            target_value = float(
                target_text.replace(",", "").replace("$", "")
            )

            if target_value <= 0:
                raise ValueError

            break
        except ValueError:
            print()
            print("Please enter a target value greater than zero.")

    analyzer = MonteCarloAnalyzer(portfolio)

    summary = analyzer.summary(
        initial_value=initial_value,
        years=years,
        simulations=simulations,
        target_value=target_value,
    )

    print()
    print("MONTE CARLO RESULTS")
    print("=" * 60)

    print(f"Portfolio             : {portfolio.name}")
    print(f"Starting Value        : ${initial_value:,.2f}")
    print(f"Projection Period     : {years} years")
    print(f"Simulations           : {simulations:,}")

    print()
    print("Projected Ending Values")
    print("-" * 60)

    print(
        f"10th Percentile       : "
        f"${summary['percentile_10']:,.2f}"
    )
    print(
        f"25th Percentile       : "
        f"${summary['percentile_25']:,.2f}"
    )
    print(
        f"Median                : "
        f"${summary['median']:,.2f}"
    )
    print(
        f"75th Percentile       : "
        f"${summary['percentile_75']:,.2f}"
    )
    print(
        f"90th Percentile       : "
        f"${summary['percentile_90']:,.2f}"
    )

    print()
    print(
        "Probability Above Starting Value: "
        f"{summary['probability_above_start']:.2%}"
    )

    if target_value is not None:
        print(
            f"Probability At or Above "
            f"${target_value:,.2f}: "
            f"{summary['probability_above_target']:.2%}"
        )

    print()
    print(
        f"Mean Ending Value     : "
        f"${summary['mean_ending_value']:,.2f}"
    )

    print()
    print(
        "Monte Carlo results are simulations based on historical "
        "monthly returns and are not forecasts or guarantees."
    )

    manager = ReportManager()

    filename = manager.create_monte_carlo_report(
        portfolio=portfolio,
        initial_value=initial_value,
        years=years,
        simulations=simulations,
        target_value=target_value,
        summary=summary,
    )

    print()
    print("Monte Carlo report created:")
    print(filename)


def analyze_loaded_portfolio(portfolio):
    """
    Analyze and report a portfolio that has already been constructed.
    """
    analyzer = PortfolioAnalyzer(portfolio)

    print()
    print("PORTFOLIO PERFORMANCE STATISTICS")
    print("=" * 60)

    print(f"CAGR                  : {analyzer.cagr():.2%}")
    print(f"Annualized Avg Return : {analyzer.annualized_return():.2%}")
    print(f"Annualized Volatility : {analyzer.annualized_volatility():.2%}")
    print(f"Maximum Drawdown      : {analyzer.max_drawdown():.2%}")
    print(f"Sharpe Ratio          : {analyzer.sharpe_ratio():.2f}")

    growth = analyzer.growth_index(10000)

    print()
    print("Growth of $10,000")
    print("-" * 60)
    print("Beginning Value : $10,000.00")
    print(f"Ending Value    : ${growth.iloc[-1]:,.2f}")

    manager = ReportManager()
    filename = manager.create_portfolio_report(portfolio)

    print()
    print("Portfolio report created:")
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
        elif choice == "7":
            manage_saved_portfolios_interactive(funds)
        elif choice == "8":
            rebalance_saved_portfolio_interactive(funds)
        elif choice == "9":
            monte_carlo_saved_portfolio_interactive()
        else:
            print()
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()
