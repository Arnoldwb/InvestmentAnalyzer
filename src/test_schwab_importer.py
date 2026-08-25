from collections import defaultdict

from investment_analyzer.importers.schwab_transaction_importer import (
    SchwabTransactionImporter,
)

CSV_FILE = (
    "/Users/arnoldbarnett/Downloads/"
    "08-Aug-2026-Buy_Sell_Transactions export-2026-08-24.csv"
)


def main():
    importer = SchwabTransactionImporter()
    transactions = importer.import_file(CSV_FILE)

    # Basic transaction counts
    assert len(transactions) == 36, f"Expected 36 transactions, got {len(transactions)}"

    buy_count = sum(t.action == "BUY" for t in transactions)

    sell_count = sum(t.action == "SELL" for t in transactions)

    assert buy_count == 20, f"Expected 20 BUY transactions, got {buy_count}"

    assert sell_count == 16, f"Expected 16 SELL transactions, got {sell_count}"

    # Calculate net shares by fund.
    net_shares = defaultdict(float)

    for transaction in transactions:
        if transaction.action == "BUY":
            net_shares[transaction.symbol] += transaction.shares
        elif transaction.action == "SELL":
            net_shares[transaction.symbol] -= transaction.shares

    expected_shares = {
        "FMFIX": 2275.748,
        "FMNEX": 852.048,
        "FMUEX": 543.782,
    }

    for symbol, expected in expected_shares.items():
        actual = net_shares[symbol]

        assert abs(actual - expected) < 0.001, (
            f"{symbol}: expected {expected:.3f}, " f"got {actual:.3f}"
        )

    # Verify chronological ordering.
    dates = [t.date for t in transactions]

    assert dates == sorted(dates), "Transactions are not in chronological order."

    # Verify first and last transactions.
    first = transactions[0]
    last = transactions[-1]

    assert first.symbol == "FMUEX"
    assert first.action == "BUY"
    assert first.shares == 669.823
    assert first.price == 3.0

    assert last.symbol == "FMUEX"
    assert last.action == "BUY"
    assert last.shares == 43.169
    assert last.price == 25.6802335

    print("Schwab importer regression test PASSED.")
    print()
    print(f"Transactions: {len(transactions)}")
    print(f"BUY:          {buy_count}")
    print(f"SELL:         {sell_count}")
    print()
    print("Net shares:")

    for symbol in sorted(expected_shares):
        print(f"  {symbol}: {net_shares[symbol]:,.3f}")


if __name__ == "__main__":
    main()
