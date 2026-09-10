from investment_analyzer.importers.vanguard_transaction_importer import (
    VanguardTransactionImporter,
)

CSV_FILE = "data/Vanguard_Import_09-01-26.csv"


def main():
    transactions = VanguardTransactionImporter.import_file(CSV_FILE)

    print()
    print("Vanguard Transaction Review")
    print("=" * 90)
    print()
    print(f"Transactions imported: {len(transactions)}")
    print()

    print(
        f"{'Date':<12} "
        f"{'Action':<22} "
        f"{'Symbol':<35} "
        f"{'Shares':>12} "
        f"{'Amount':>12}"
    )
    print("-" * 90)

    for transaction in transactions:
        print(
            f"{transaction.date!s:<12} "
            f"{transaction.action:<22} "
            f"{transaction.symbol:<35} "
            f"{transaction.shares:>12.3f} "
            f"{transaction.amount:>12.2f}"
        )

    print()
    print("Transaction review complete.")


if __name__ == "__main__":
    main()
