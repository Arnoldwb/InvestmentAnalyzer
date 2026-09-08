import pandas as pd

from investment_analyzer.core.historical_cash_history import (
    transaction_cash_effect,
)
from investment_analyzer.importers.vanguard_transaction_importer import (
    VanguardTransactionImporter,
)


CSV_FILE = "data/Vanguard_Import_09-01-26.csv"


def main():
    transactions = VanguardTransactionImporter.import_file(CSV_FILE)

    daily_effects = {}

    for transaction in transactions:
        daily_effects[transaction.date] = (
            daily_effects.get(transaction.date, 0.0)
            + transaction_cash_effect(transaction)
        )

    cash = 0.0
    reconstructed = []

    for transaction_date in sorted(daily_effects):
        cash += daily_effects[transaction_date]

        reconstructed.append(
            {
                "Date": pd.Timestamp(transaction_date),
                "Cash": cash,
            }
        )

    reconstructed = pd.DataFrame(reconstructed)

    vanguard = pd.read_csv(CSV_FILE)

    vanguard = vanguard[vanguard["Date"].notna()].copy()

    vanguard["Date"] = pd.to_datetime(
        vanguard["Date"],
        format="%m/%d/%y",
    )

    vanguard["Balance"] = pd.to_numeric(
        vanguard["Balance"].astype(str).str.replace(",", ""),
        errors="coerce",
    )

    expected = (
        vanguard[vanguard["Balance"].notna()]
        [["Date", "Balance"]]
        .groupby("Date", as_index=False)
        .last()
        .sort_values("Date")
        .reset_index(drop=True)
    )

    comparison = pd.merge(
        expected,
        reconstructed,
        on="Date",
        how="outer",
    )

    comparison["Difference"] = (
        comparison["Cash"] - comparison["Balance"]
    )

    mismatches = comparison[
        comparison["Difference"].abs() > 0.01
    ]

    assert mismatches.empty, (
        "Vanguard daily cash reconciliation failed:\n"
        + mismatches.to_string(index=False)
    )

    print("Vanguard cash reconciliation regression test PASSED.")
    print()
    print("Transactions:", len(transactions))
    print("Dates checked:", len(comparison))
    print(f"Final reconstructed cash: {cash:.2f}")
    print(f"Final Vanguard balance: {expected['Balance'].iloc[-1]:.2f}")


if __name__ == "__main__":
    main()
