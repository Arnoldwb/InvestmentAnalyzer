from investment_analyzer.core.paths import DATA_DIR


def discover_funds():
    """
    Return a sorted list of fund symbols based on CSV files
    found in the project's data folder.
    """

    funds = sorted(
        csv_file.stem
        for csv_file in DATA_DIR.glob("*.csv")
    )

    return funds