import pandas as pd


investment_history = pd.DataFrame(
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
        "Portfolio Value": [
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
                "2020-01-01",
                "2020-01-03",
            ]
        ),
        "Cash": [
            10000.0,
            12000.0,
        ],
    }
)

aligned = pd.merge_asof(
    investment_history.sort_values("Date"),
    cash_history.sort_values("Date"),
    on="Date",
    direction="backward",
)

expected = [10000.0, 10000.0, 12000.0, 12000.0, 12000.0]

assert aligned["Cash"].tolist() == expected

print("Historical cash alignment test PASSED.")
print(aligned.to_string(index=False))
