from pathlib import Path
import tempfile

from investment_analyzer.core.fund_library import FundLibrary


def make_valid_csv(path: Path):
    lines = [
        "Date,Adj Close"
    ]

    for month in range(25):
        year = 2024 + (month // 12)
        month_number = (month % 12) + 1

        lines.append(
            f"01-{month_number:02d}-{year},"
            f"{100 + month:.2f}"
        )

    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def test_usable_symbols_excludes_invalid_funds():
    with tempfile.TemporaryDirectory() as folder:
        data_dir = Path(folder)
        portfolio_dir = data_dir / "portfolios"
        portfolio_dir.mkdir()

        make_valid_csv(
            data_dir / "GOOD.csv"
        )

        (data_dir / "BAD.csv").write_text(
            "Date,Adj Close\n"
            "01-Jan-25,BAD\n",
            encoding="utf-8",
        )

        library = FundLibrary(
            data_dir=data_dir,
            portfolio_dir=portfolio_dir,
        )

        symbols = library.usable_symbols()

        assert symbols == ["GOOD"]

        print(
            "PASS: Usable fund selection excludes "
            "invalid funds."
        )


if __name__ == "__main__":
    test_usable_symbols_excludes_invalid_funds()
    print(
        "PASS: FundLibrary test completed."
    )
