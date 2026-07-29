from pathlib import Path


def discover_funds():
    """
    Return a sorted list of fund symbols based on CSV files
    found in the project's data folder.
    """

    project_root = Path(__file__).resolve().parents[3]
    data_folder = project_root / "data"

    funds = sorted(
        csv_file.stem
        for csv_file in data_folder.glob("*.csv")
    )

    return funds