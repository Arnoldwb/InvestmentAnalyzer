from investment_analyzer.core.historical_reconstruction import (
    reconstruct_shares,
)
from investment_analyzer.core.paths import DATA_DIR
from investment_analyzer.core.vanguard_historical_importer import (
    import_vanguard_history,
)

CSV_FILE = DATA_DIR / "Vanguard_Import_09-01-26.csv"


def main():
    starting_positions, events = import_vanguard_history(CSV_FILE)

    assert len(starting_positions) == 1, (
        f"Expected 1 starting position, got {len(starting_positions)}"
    )

    expected_starting_shares = {
        "Vanguard Health Care-Admiral": 1502.471,
    }

    for position in starting_positions:
        expected = expected_starting_shares[position.symbol]
        assert abs(position.shares - expected) < 0.001, (
            f"{position.symbol}: expected {expected:.3f}, "
            f"got {position.shares:.3f}"
        )

    assert len(events) == 8, f"Expected 8 events, got {len(events)}"

    event_types = [event.event_type for event in events]

    assert event_types.count("BUY") == 3
    assert event_types.count("SELL") == 4
    assert event_types.count("REINVEST") == 1
    assert event_types.count("ADD") == 0
    assert event_types.count("REMOVE") == 0

    investment_events = events

    balances = reconstruct_shares(
        starting_positions,
        investment_events,
    )

    expected_balances = {
        "Vanguard Federal Money Market Fund": 0.0,
        "Vanguard Health Care-Admiral": 0.0,
        "Vanguard Wellington Admiral": 1389.896,
    }

    for symbol, expected in expected_balances.items():
        actual = balances.get(symbol, 0.0)

        assert abs(actual - expected) < 0.001, (
            f"{symbol}: expected {expected:.3f}, "
            f"got {actual:.3f}"
        )

    print("Vanguard historical importer regression test PASSED.")
    print()
    print(f"Starting positions: {len(starting_positions)}")
    print(f"Historical events:  {len(events)}")
    print(f"Events used:        {len(investment_events)}")
    print()
    print("Reconstructed shares:")

    for symbol in sorted(expected_balances):
        print(f"  {symbol}: {balances.get(symbol, 0.0):,.3f}")


if __name__ == "__main__":
    main()
