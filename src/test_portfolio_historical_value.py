import pandas as pd

from investment_analyzer.models.portfolio import Portfolio

from investment_analyzer.core.vanguard_historical_importer import (
    import_vanguard_history,
)


CSV_FILE = "data/Vanguard_Import_09-01-26.csv"


def main():
    starting_positions, events = import_vanguard_history(CSV_FILE)

    # Exclude the known Vanguard bookkeeping reconciliation pair
    # from this historical reconstruction test.
    events = [
        event
        for event in events
        if not (
            event.date.isoformat() == "2026-04-20"
            and event.event_type in {"ADD", "REMOVE"}
        )
    ]

    portfolio = Portfolio(name="Vanguard Historical Test")

    portfolio.historical_starting_positions.extend(
        starting_positions
    )

    portfolio.historical_events.extend(events)

    value_history = portfolio.historical_value_history()

    assert not value_history.empty

    assert list(value_history.columns) == [
        "Date",
        "Symbol",
        "Shares",
        "Price",
        "Value",
    ]

    assert set(value_history["Symbol"]) == {
        "VWENX",
        "VGHAX",
    }

    assert len(value_history) == 940

    first_date = value_history.iloc[0]

    assert first_date["Date"] == pd.Timestamp("2024-09-25")

    print("Portfolio historical value integration test PASSED.")
    print()
    print("Portfolio:", portfolio.name)
    print("Rows:", len(value_history))
    print()
    print(value_history.head(4).to_string(index=False))


if __name__ == "__main__":
    main()
