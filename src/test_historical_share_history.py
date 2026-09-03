from investment_analyzer.core.historical_reconstruction import (
    reconstruct_shares,
)
from investment_analyzer.core.historical_share_history import (
    reconstruct_share_history,
)
from investment_analyzer.core.paths import DATA_DIR
from investment_analyzer.core.vanguard_historical_importer import (
    import_vanguard_history,
)

CSV_FILE = DATA_DIR / "Vanguard_Import_09-01-26.csv"


def main():
    starting_positions, events = import_vanguard_history(CSV_FILE)

    history = reconstruct_share_history(
        starting_positions,
        events,
    )

    assert not history.empty

    assert list(history.columns) == [
        "Date",
        "Symbol",
        "Shares",
    ]

    # The Health Care placeholder establishes the initial balance.
    first_health = history[
        (history["Symbol"] == "Vanguard Health Care-Admiral")
        & (history["Date"] == "2024-09-25")
    ]

    assert len(first_health) == 1
    assert abs(first_health.iloc[0]["Shares"] - 1502.471) < 0.001

    # Wellington enters the historical record through its actual
    # December 23, 2024 purchase.
    first_wellington = history[
        (history["Symbol"] == "Vanguard Wellington Admiral")
        & (history["Date"] == "2024-12-23")
    ]

    assert len(first_wellington) == 1
    assert abs(first_wellington.iloc[0]["Shares"] - 1384.153) < 0.001

    # The importer now handles the April 2026 reconciliation pair,
    # so the reconstructed history can be used directly.
    expected_balances = reconstruct_shares(
        starting_positions,
        events,
    )

    clean_history = history

    for symbol, expected in expected_balances.items():
        symbol_history = clean_history[
            clean_history["Symbol"] == symbol
        ]

        assert not symbol_history.empty

        actual = symbol_history.iloc[-1]["Shares"]

        assert abs(actual - expected) < 0.001, (
            f"{symbol}: expected {expected:.3f}, " f"got {actual:.3f}"
        )

    print("Historical share history regression test PASSED.")
    print()
    print(f"History rows: {len(history)}")
    print()
    print("Final reconstructed balances:")

    for symbol in sorted(expected_balances):
        symbol_history = clean_history[
            clean_history["Symbol"] == symbol
        ]

        actual = symbol_history.iloc[-1]["Shares"]

        print(f"  {symbol}: {actual:,.3f}")


if __name__ == "__main__":
    main()
