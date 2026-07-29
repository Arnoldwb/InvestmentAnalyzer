from investment_analyzer.core.file_discovery import discover_funds

from loader import load_fund
from returns import monthly_returns
from charts import growth_chart
from report import save_report

from statistics import (
    fund_statistics,
    cagr,
    max_drawdown,
    best_year,
    worst_year,
    positive_years,
    negative_years,
)

from ranking import (
    print_rankings,
    print_executive_summary,
    print_recommendation,
)


def main():

    funds = discover_funds()

    print()
    print("=" * 60)
    print("Investment Analyzer")
    print("=" * 60)

    if not funds:
        print("No CSV files were found in the data folder.")
        return

    print(f"\nFound {len(funds)} fund(s):\n")

    for fund in funds:
        print(f"  {fund}")

    print()

    fund_returns = {}
    results = {}

    for symbol in funds:

        df = load_fund(symbol)

        r = monthly_returns(df)

        fund_returns[symbol] = r

        stats = fund_statistics(r)

        results[symbol] = {
            "CAGR": cagr(df),
            "Return": stats["Annualized Return"],
            "Volatility": stats["Annualized Volatility"],
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

    print()
    print("=" * 80)

    print_rankings(results)
    print_executive_summary(results)
    print_recommendation(results)


if __name__ == "__main__":
    main()