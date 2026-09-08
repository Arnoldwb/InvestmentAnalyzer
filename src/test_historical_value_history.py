import pandas as pd

from investment_analyzer.core.historical_share_history import (
    reconstruct_share_history,
)
from investment_analyzer.core.historical_value_history import (
    calculate_historical_value_history,
)
from investment_analyzer.core.vanguard_historical_importer import (
    import_vanguard_history,
)

CSV_FILE = "data/Vanguard_Import_09-01-26.csv"


def main():
    starting_positions, events = import_vanguard_history(CSV_FILE)

    share_history = reconstruct_share_history(
        starting_positions,
        events,
    )

    value_history = calculate_historical_value_history(share_history)

    assert list(value_history.columns) == [
        "Date",
        "Symbol",
        "Shares",
        "Price",
        "Value",
    ]

    assert not value_history.empty

    assert set(value_history["Symbol"]) == {
        "VWENX",
        "VGHAX",
        "VMFXX",
    }

    assert value_history["Shares"].notna().all()
    assert value_history["Price"].notna().all()
    assert value_history["Value"].notna().all()

    # The first historical VWENX value should reflect the actual
    # opening transaction on December 23, 2024.
    first_wellington = value_history[value_history["Symbol"] == "VWENX"].iloc[0]

    assert first_wellington["Date"] == pd.Timestamp("2024-12-23")
    assert abs(first_wellington["Shares"] - 1384.153) < 0.001
    assert (
        abs(
            first_wellington["Value"]
            - first_wellington["Shares"] * first_wellington["Price"]
        )
        < 0.01
    )

    # Verify that values are calculated from shares multiplied by price.
    calculated_values = value_history["Shares"] * value_history["Price"]

    assert ((value_history["Value"] - calculated_values).abs() < 0.01).all()

    print("Historical value history regression test PASSED.")
    print()
    print("Rows:", len(value_history))
    print()
    print("First rows:")
    print(value_history.head(6).to_string(index=False))


if __name__ == "__main__":
    main()
