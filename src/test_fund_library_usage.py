from pathlib import Path
import json
import tempfile

from investment_analyzer.core.fund_library import FundLibrary


def make_valid_csv(path: Path):
    lines = ["Date,Adj Close"]

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


def test_fund_library_detects_portfolio_usage():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        data_dir = root / "data"
        portfolio_dir = root / "portfolios"

        data_dir.mkdir()
        portfolio_dir.mkdir()

        make_valid_csv(data_dir / "GOOD.csv")

        portfolio = {
            "name": "Test Portfolio",
            "holdings": [
                {
                    "symbol": "GOOD",
                    "allocation": 100.0,
                }
            ],
        }

        (portfolio_dir / "test_portfolio.json").write_text(
            json.dumps(portfolio),
            encoding="utf-8",
        )

        library = FundLibrary(
            data_dir=data_dir,
            portfolio_dir=portfolio_dir,
        )

        entry = library.get("GOOD")

        assert entry is not None
        assert entry.used_by == ["Test Portfolio"]
        assert entry.portfolio_count == 1
        assert library.portfolios_using("GOOD") == [
            "Test Portfolio"
        ]
