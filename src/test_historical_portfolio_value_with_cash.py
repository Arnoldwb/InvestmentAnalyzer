import pandas as pd

from investment_analyzer.core.historical_portfolio_value import (
    calculate_historical_portfolio_value,
)


value_history = pd.DataFrame(
    {
        "Date": pd.to_datetime(
            [
                "2020-01-01",
                "2020-01-02",
                "2020-01-03",
                "2020-01-04",
                "2020-01-05",
            ]
        ),
        "Symbol": ["VBIAX"] * 5,
        "Value": [
            100000.0,
            100500.0,
            101000.0,
            101500.0,
            102000.0,
        ],
    }
)

cash_history = pd.DataFrame(
    {
        "Date": pd.to_datetime(
            [
                "2020-01-02",
                "2020-01-04",
            ]
        ),
        "Cash": [
            10000.0,
            12000.0,
        ],
    }
)

portfolio_history = calculate_historical_portfolio_value(
    value_history,
    cash_history,
)

expected_dates = pd.to_datetime(
    [
        "2020-01-02",
        "2020-01-03",
        "2020-01-04",
        "2020-01-05",
    ]
)

expected_values = [
    110500.0,
    111000.0,
    113500.0,
    114000.0,
]

assert portfolio_history["Date"].tolist() == expected_dates.tolist()
assert portfolio_history["Portfolio Value"].tolist() == expected_values

print("Historical portfolio value with cash test PASSED.")
print(portfolio_history.to_string(index=False))
