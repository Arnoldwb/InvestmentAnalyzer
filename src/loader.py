from pathlib import Path

import pandas as pd

# Project folder

PROJECT = Path(__file__).resolve().parent.parent

# Data folder

DATA = PROJECT / "data"

def load_fund(symbol):

    """Load and clean one Yahoo Finance CSV file."""

    filename = DATA / f"{symbol}.csv"

    print(f"Loading {filename.name}")

    # Read the CSV

    df = pd.read_csv(filename)

    # Clean the column names

    df.columns = (

        df.columns

        .str.replace("\u00A0", "", regex=False)

        .str.strip()

    )

    # Convert Date to a real date

    df["Date"] = pd.to_datetime(
    df["Date"],
    format="%d-%b-%y",
    errors="coerce"
)

    # Convert Adjusted Close to a number

    df["Adj Close"] = pd.to_numeric(df["Adj Close"], errors="coerce")

    # Remove bad rows

    df = df.dropna(subset=["Date", "Adj Close"])

    # Sort oldest to newest

    df = df.sort_values("Date").reset_index(drop=True)

    return df