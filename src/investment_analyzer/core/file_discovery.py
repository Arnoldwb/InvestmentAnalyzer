from investment_analyzer.core.paths import DATA_DIR
import pandas as pd


def discover_funds():
    """
    Return a sorted list of fund symbols based on valid historical
    price CSV files found in the project's data folder.

    A valid fund CSV must contain an 'Adj Close' column.
    """

    funds = []

    for csv_file in DATA_DIR.glob("*.csv"):
        try:
            columns = pd.read_csv(csv_file, nrows=0).columns

            if "Adj Close" in columns:
                funds.append(csv_file.stem)

        except Exception:
            # Ignore CSV files that cannot be read as fund data.
            continue

    return sorted(funds)
