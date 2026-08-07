from datetime import date, timedelta
from pathlib import Path
import shutil
import tempfile

from investment_analyzer.core.fund_data_validator import (
    FundDataValidator,
)


def make_valid_csv(path, start_date=date(2025, 1, 1), rows=24):
    lines = [
        "Date,Open,High,Low,Close,Adj Close,Volume"
    ]

    for number in range(rows):
        current_date = (
            start_date + timedelta(days=number)
        )
        price = 100 + number

        lines.append(
            f"{current_date.strftime('%d-%b-%y')},"
            f"{price},{price + 1},{price - 1},"
            f"{price},{price},1000"
        )

    path.write_text("\n".join(lines) + "\n")


def test_valid_csv():
    root = Path(
        tempfile.mkdtemp(
            prefix="validator_valid_"
        )
    )

    try:
        file = root / "TEST.csv"
        make_valid_csv(file)

        result = FundDataValidator().validate(file)

        assert result.valid
        assert result.usable_rows == 24
        assert result.first_date is not None
        assert result.last_date is not None

        print("PASS: Valid CSV was accepted.")

    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_missing_required_column():
    root = Path(
        tempfile.mkdtemp(
            prefix="validator_missing_"
        )
    )

    try:
        file = root / "TEST.csv"

        file.write_text(
            "Date,Open,High,Low,Close,Volume\n"
            "01-Jan-25,100,101,99,100,1000\n"
        )

        result = FundDataValidator().validate(file)

        assert not result.valid
        assert any(
            "Missing required column" in error
            for error in result.errors
        )

        print(
            "PASS: Missing required column was rejected."
        )

    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_invalid_date():
    root = Path(
        tempfile.mkdtemp(
            prefix="validator_date_"
        )
    )

    try:
        file = root / "TEST.csv"
        make_valid_csv(file)

        text = file.read_text()
        text = text.replace(
            "01-Jan-25",
            "NOT-A-DATE",
            1,
        )
        file.write_text(text)

        result = FundDataValidator().validate(file)

        assert not result.valid
        assert any(
            "invalid or missing Date" in error
            for error in result.errors
        )

        print("PASS: Invalid date was rejected.")

    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_invalid_adj_close():
    root = Path(
        tempfile.mkdtemp(
            prefix="validator_price_"
        )
    )

    try:
        file = root / "TEST.csv"
        make_valid_csv(file)

        text = file.read_text()
        lines = text.splitlines()
        lines[1] = lines[1].replace(
            ",100,100,",
            ",BAD,BAD,",
        )
        file.write_text("\n".join(lines) + "\n")

        result = FundDataValidator().validate(file)

        assert not result.valid
        assert any(
            "invalid or missing Adj Close" in error
            for error in result.errors
        )

        print(
            "PASS: Invalid Adj Close was rejected."
        )

    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_duplicate_dates():
    root = Path(
        tempfile.mkdtemp(
            prefix="validator_duplicate_"
        )
    )

    try:
        file = root / "TEST.csv"
        make_valid_csv(file)

        text = file.read_text()
        lines = text.splitlines()

        lines[2] = lines[1]

        file.write_text(
            "\n".join(lines) + "\n"
        )

        result = FundDataValidator().validate(file)

        assert not result.valid
        assert any(
            "duplicate Date" in error
            for error in result.errors
        )

        print(
            "PASS: Duplicate dates were rejected."
        )

    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_insufficient_history():
    root = Path(
        tempfile.mkdtemp(
            prefix="validator_short_"
        )
    )

    try:
        file = root / "TEST.csv"
        make_valid_csv(file, rows=10)

        result = FundDataValidator().validate(file)

        assert not result.valid
        assert any(
            "Insufficient usable history" in error
            for error in result.errors
        )

        print(
            "PASS: Insufficient history was rejected."
        )

    finally:
        shutil.rmtree(root, ignore_errors=True)


def test_newest_first_warning():
    root = Path(
        tempfile.mkdtemp(
            prefix="validator_newest_"
        )
    )

    try:
        file = root / "TEST.csv"
        make_valid_csv(file)

        lines = file.read_text().splitlines()

        header = lines[0]
        data = lines[1:]

        data.reverse()

        file.write_text(
            "\n".join(
                [header] + data
            ) + "\n"
        )

        result = FundDataValidator().validate(file)

        assert result.valid
        assert any(
            "newest-first" in warning
            for warning in result.warnings
        )

        print(
            "PASS: Newest-first data was accepted "
            "with warning."
        )

    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    test_valid_csv()
    test_missing_required_column()
    test_invalid_date()
    test_invalid_adj_close()
    test_duplicate_dates()
    test_insufficient_history()
    test_newest_first_warning()

    print(
        "PASS: FundDataValidator test suite completed."
    )
