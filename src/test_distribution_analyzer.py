from pathlib import Path

from investment_analyzer.analysis.distribution_analyzer import (
    DistributionAnalyzer,
)
from investment_analyzer.importers.quicken_transaction_importer import (
    QuickenTransactionImporter,
)
from investment_analyzer.models.portfolio import Portfolio

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main():
    transaction_file = (
        PROJECT_ROOT
        / "transactions"
        / "historical"
        / "Export-VANGUARD_2026-09-04csv.csv"
    )

    importer = QuickenTransactionImporter()

    transactions = importer.import_file(transaction_file)

    portfolio = Portfolio(
        name="Distribution Test Portfolio",
    )

    portfolio.transactions.extend(transactions)

    analyzer = DistributionAnalyzer(portfolio)

    distributions = analyzer.distributions()

    assert not distributions.empty

    assert set(distributions["Type"]) == {
        "Dividend",
        "Capital Gain",
    }

    summary = analyzer.summary_by_fund()

    vghax = summary.loc[summary["Symbol"] == "VGHAX"].iloc[0]

    assert vghax["Dividends"] == 1084.63
    assert vghax["Capital Gains"] == 9760.75
    assert vghax["Total Distributions"] == 10845.38

    vwenx = summary.loc[summary["Symbol"] == "VWENX"].iloc[0]

    assert vwenx["Dividends"] == 3743.64
    assert vwenx["Capital Gains"] == 18571.29
    assert vwenx["Total Distributions"] == 22314.93

    vmfxx = summary.loc[summary["Symbol"] == "VMFXX"].iloc[0]

    assert vmfxx["Dividends"] == 9.91
    assert vmfxx["Capital Gains"] == 0.0
    assert vmfxx["Total Distributions"] == 9.91

    # Reinvestment transactions must not be counted
    # as additional distributions.
    assert (
        len(distributions[distributions["Type"].isin(["Dividend", "Capital Gain"])])
        == 14
    )

    print("Distribution analyzer test PASSED.")
    print()
    print(summary.to_string(index=False))
    print()
    print(
        "Total distributions:",
        f"${summary['Total Distributions'].sum():,.2f}",
    )


if __name__ == "__main__":
    main()
