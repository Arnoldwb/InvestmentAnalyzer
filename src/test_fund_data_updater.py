from datetime import date, timedelta
from pathlib import Path
import shutil
import tempfile

from investment_analyzer.core.fund_data_updater import (
    FundDataUpdater,
)


class FakeTiingoClient:
    """Fake Tiingo service used for safe local testing."""

    def get_metadata(self, symbol):
        assert symbol == "TEST"
        return {
            "endDate": "2026-08-05",
        }

    def get_prices(
        self,
        symbol,
        start_date=None,
        end_date=None,
    ):
        assert symbol == "TEST"

        return [
            {
                "date": "2026-08-04T00:00:00.000Z",
                "open": 124.0,
                "high": 125.0,
                "low": 123.0,
                "close": 124.5,
                "adjClose": 124.5,
                "volume": 1000,
            },
            {
                "date": "2026-08-05T00:00:00.000Z",
                "open": 125.0,
                "high": 126.0,
                "low": 124.0,
                "close": 125.5,
                "adjClose": 125.5,
                "volume": 1100,
            },
        ]


def test_safe_tiingo_update():
    test_root = Path(
        tempfile.mkdtemp(
            prefix="investment_analyzer_test_"
        )
    )

    try:
        data_dir = test_root / "data"
        backup_dir = test_root / "backups"

        data_dir.mkdir()
        backup_dir.mkdir()

        fund_file = data_dir / "TEST.csv"

        start_date = date(2026, 7, 11)

        rows = [
            "Date,Open,High,Low,Close,Adj Close,Volume"
        ]

        for number in range(24):
            current_date = (
                start_date
                + timedelta(days=number)
            )

            price = 100 + number

            rows.append(
                f"{current_date.strftime('%d-%b-%y')},"
                f"{price},{price + 1},{price - 1},"
                f"{price},{price},1000"
            )

        fund_file.write_text(
            "\n".join(rows) + "\n"
        )

        updater = FundDataUpdater(
            client=FakeTiingoClient(),
            data_dir=data_dir,
            backup_dir=backup_dir,
        )

        preview = updater.preview_update("TEST")

        assert preview.update_available
        assert preview.new_rows == 2

        result = updater.apply_update(
            "TEST",
            preview=preview,
        )

        assert result.updated
        assert result.rows_added == 2

        assert result.backup is not None
        assert result.backup.exists()

        assert fund_file.exists()

        lines = fund_file.read_text().splitlines()

        assert len(lines) == 27

        assert "04-Aug-26" in lines[25]
        assert "05-Aug-26" in lines[26]

        assert result.validation is not None
        assert result.validation.valid

        print("PASS: Tiingo preview detected 2 new rows.")
        print("PASS: Update added exactly 2 rows.")
        print("PASS: Existing historical data was preserved.")
        print("PASS: Backup was created.")
        print("PASS: Updated CSV passed validation.")
        print("PASS: Safe Tiingo updater test completed.")

    finally:
        shutil.rmtree(
            test_root,
            ignore_errors=True,
        )




class BadTiingoClient:
    """Fake Tiingo service that returns invalid update data."""

    def get_metadata(self, symbol):
        return {
            "endDate": "2026-08-05",
        }

    def get_prices(
        self,
        symbol,
        start_date=None,
        end_date=None,
    ):
        return [
            {
                "date": "2026-08-04T00:00:00.000Z",
                "open": 200.0,
                "high": 201.0,
                "low": 199.0,
                "close": 200.0,
                "adjClose": None,
                "volume": 1000,
            },
        ]


def test_invalid_update_does_not_replace_original():
    test_root = Path(
        tempfile.mkdtemp(
            prefix="investment_analyzer_test_bad_"
        )
    )

    try:
        data_dir = test_root / "data"
        backup_dir = test_root / "backups"

        data_dir.mkdir()
        backup_dir.mkdir()

        fund_file = data_dir / "TEST.csv"

        start_date = date(2026, 7, 11)

        rows = [
            "Date,Open,High,Low,Close,Adj Close,Volume"
        ]

        for number in range(24):
            current_date = (
                start_date
                + timedelta(days=number)
            )

            price = 100 + number

            rows.append(
                f"{current_date.strftime('%d-%b-%y')},"
                f"{price},{price + 1},{price - 1},"
                f"{price},{price},1000"
            )

        original_contents = (
            "\n".join(rows) + "\n"
        )

        fund_file.write_text(
            original_contents
        )

        updater = FundDataUpdater(
            client=BadTiingoClient(),
            data_dir=data_dir,
            backup_dir=backup_dir,
        )

        preview = updater.preview_update("TEST")

        assert preview.update_available
        assert preview.new_rows == 1

        try:
            updater.apply_update(
                "TEST",
                preview=preview,
            )
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Expected invalid update to be rejected."
            )

        assert fund_file.read_text() == original_contents

        assert not list(
            backup_dir.glob("TEST_*.csv")
        )

        print(
            "PASS: Invalid update was rejected."
        )
        print(
            "PASS: Original CSV remained unchanged."
        )
        print(
            "PASS: No backup was created for the rejected update."
        )
        print(
            "PASS: Invalid update safety test completed."
        )

    finally:
        shutil.rmtree(
            test_root,
            ignore_errors=True,
        )


if __name__ == "__main__":
    test_safe_tiingo_update()
    test_invalid_update_does_not_replace_original()
