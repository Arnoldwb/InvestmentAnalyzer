import pandas as pd

from investment_analyzer.core.historical_portfolio_value import (
    calculate_historical_portfolio_value,
)


def main():
    value_history = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-09-25",
                    "2024-09-25",
                    "2024-09-26",
                    "2024-09-26",
                    "2024-09-27",
                    "2024-09-27",
                ]
            ),
            "Symbol": [
                "VGHAX",
                "VWENX",
                "VGHAX",
                "VWENX",
                "VGHAX",
                "VWENX",
            ],
            "Value": [
                120798.66840,
                89912.37224,
                116920.37500,
                90120.85664,
                116441.66875,
                90093.05872,
            ],
        }
    )

    portfolio_history = calculate_historical_portfolio_value(
        value_history
    )

    assert list(portfolio_history.columns) == [
        "Date",
        "Portfolio Value",
    ]

    assert len(portfolio_history) == 3

    assert (
        portfolio_history.iloc[0]["Date"]
        == pd.Timestamp("2024-09-25")
    )

    assert abs(
        portfolio_history.iloc[0]["Portfolio Value"]
        - (120798.66840 + 89912.37224)
    ) < 0.01

    assert abs(
        portfolio_history.iloc[1]["Portfolio Value"]
        - (116920.37500 + 90120.85664)
    ) < 0.01

    assert abs(
        portfolio_history.iloc[2]["Portfolio Value"]
        - (116441.66875 + 90093.05872)
    ) < 0.01

    # Verify chronological ordering.
    assert portfolio_history["Date"].is_monotonic_increasing

    # Verify empty input behavior.
    empty = calculate_historical_portfolio_value(
        pd.DataFrame(
            columns=["Date", "Symbol", "Value"]
        )
    )

    assert list(empty.columns) == [
        "Date",
        "Portfolio Value",
    ]

    assert empty.empty

    print("Historical portfolio value regression test PASSED.")
    print()
    print(portfolio_history.to_string(index=False))


if __name__ == "__main__":
    main()
