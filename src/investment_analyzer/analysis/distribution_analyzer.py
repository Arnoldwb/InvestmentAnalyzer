from dataclasses import dataclass

import pandas as pd

from investment_analyzer.models.transaction import (
    TransactionAction,
)


@dataclass
class DistributionAnalyzer:
    """
    Analyze dividend and capital-gain distributions
    recorded in a portfolio transaction ledger.
    """

    portfolio: object

    def distributions(self) -> pd.DataFrame:
        """
        Return all dividend and capital-gain distributions.

        Reinvestment transactions are intentionally excluded.
        They represent the disposition of a distribution rather
        than a separate distribution.
        """

        records = []

        for transaction in self.portfolio.transactions:
            if transaction.action == TransactionAction.DIVIDEND:
                distribution_type = "Dividend"

            elif transaction.action in {
                TransactionAction.CAPITAL_GAIN,
                "CAPITAL_GAIN",
            }:
                distribution_type = "Capital Gain"

            else:
                continue

            records.append(
                {
                    "Date": pd.Timestamp(transaction.date),
                    "Symbol": transaction.symbol,
                    "Type": distribution_type,
                    "Amount": float(transaction.amount),
                }
            )

        return pd.DataFrame(
            records,
            columns=[
                "Date",
                "Symbol",
                "Type",
                "Amount",
            ],
        )

    def summary_by_fund(self) -> pd.DataFrame:
        """
        Summarize distributions by investment.
        """

        distributions = self.distributions()

        if distributions.empty:
            return pd.DataFrame(
                columns=[
                    "Symbol",
                    "Dividends",
                    "Capital Gains",
                    "Total Distributions",
                ]
            )

        summary = (
            distributions.assign(
                Dividends=distributions["Amount"].where(
                    distributions["Type"] == "Dividend",
                    0.0,
                ),
                Capital_Gains=distributions["Amount"].where(
                    distributions["Type"] == "Capital Gain",
                    0.0,
                ),
            )
            .groupby("Symbol", as_index=False)
            .agg(
                Dividends=("Dividends", "sum"),
                Capital_Gains=("Capital_Gains", "sum"),
            )
        )

        summary["Dividends"] = summary["Dividends"].round(2)
        summary["Capital_Gains"] = summary["Capital_Gains"].round(2)

        summary = summary.rename(
            columns={
                "Capital_Gains": "Capital Gains",
            }
        )

        summary["Total Distributions"] = (
            summary["Dividends"] + summary["Capital Gains"]
        ).round(2)

        return summary[
            [
                "Symbol",
                "Dividends",
                "Capital Gains",
                "Total Distributions",
            ]
        ]
