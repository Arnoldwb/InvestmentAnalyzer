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

    # The two starting positions must establish the first balances.
    first_wellington = history[
        (history["Symbol"] == "Vanguard Wellington Admiral")
        & (history["Date"] == "2024-09-25")
    ]

    assert len(first_wellington) == 1
    assert abs(first_wellington.iloc[0]["Shares"] - 1389.896) < 0.001

    first_health = history[
        (history["Symbol"] == "Vanguard Health Care-Admiral")
        & (history["Date"] == "2024-09-25")
    ]

    assert len(first_health) == 1
    assert abs(first_health.iloc[0]["Shares"] - 1502.471) < 0.001

    # Verify the final chronological balances, excluding the April
    # reconciliation pair just as the importer regression test does.
    investment_events = [
        event
        for event in events
        if not (
            event.date.isoformat() == "2026-04-20"
            and event.symbol == "Vanguard Wellington Admiral"
            and event.event_type in {"ADD", "REMOVE"}
        )
    ]

    expected_balances = reconstruct_shares(
        starting_positions,
        investment_events,
    )

    # Rebuild the history without the reconciliation pair so the final
    # history row represents the same investment history being tested.
    clean_history = reconstruct_share_history(
        starting_positions,
        investment_events,
    )

    for symbol, expected in expected_balances.items():
        symbol_history = clean_history[
            clean_history["Symbol"] == symbol
        ]

        assert not symbol_history.empty

        actual = symbol_history.iloc[-1]["Shares"]

        assert abs(actual - expected) < 0.001, (
            f"{symbol}: expected {expected:.3f}, "
            f"got {actual:.3f}"
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
