from pathlib import Path
import tempfile

from investment_analyzer.core.file_discovery import discover_funds


with tempfile.TemporaryDirectory() as folder:
    data_dir = Path(folder)

    # Create several CSV files in deliberately unsorted order.
    for symbol in ["ZZZZ", "AAAA", "MMMM"]:
        (data_dir / f"{symbol}.csv").write_text(
            "Date,Adj Close\n"
            "01-Jan-24,100.00\n",
            encoding="utf-8",
        )

    # Non-CSV files must not be treated as funds.
    (data_dir / "README.txt").write_text(
        "Not a fund.",
        encoding="utf-8",
    )

    (data_dir / "notes.json").write_text(
        "{}",
        encoding="utf-8",
    )

    # Temporarily replace the module's DATA_DIR.
    import investment_analyzer.core.file_discovery as file_discovery

    original_data_dir = file_discovery.DATA_DIR

    try:
        file_discovery.DATA_DIR = data_dir

        funds = discover_funds()

        assert funds == ["AAAA", "MMMM", "ZZZZ"]
        assert "README" not in funds
        assert "notes" not in funds

        print("PASS: Fund discovery finds CSV files dynamically.")
        print("PASS: Fund discovery returns symbols in sorted order.")

    finally:
        file_discovery.DATA_DIR = original_data_dir
