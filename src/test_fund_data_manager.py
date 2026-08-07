import json
import tempfile
from pathlib import Path

import pandas as pd

from investment_analyzer.core.fund_data_manager import (
    FundDataManager,
)


def write_csv(path, rows):
    data = pd.DataFrame(rows)
    data.to_csv(path, index=False)


with tempfile.TemporaryDirectory() as folder:
    root = Path(folder)
    data_dir = root / "data"
    portfolio_dir = root / "portfolios"

    data_dir.mkdir()
    portfolio_dir.mkdir()

    manager = FundDataManager(
        data_dir=data_dir,
        portfolio_dir=portfolio_dir,
    )

    valid_rows = [
        {
            "Date": "01-Jan-24",
            "Open": 50.00,
            "High": 50.50,
            "Low": 49.50,
            "Close": 50.00,
            "Adj Close": 50.00,
            "Volume": "-",
        },
        {
            "Date": "01-Feb-24",
            "Open": 51.00,
            "High": 51.50,
            "Low": 50.50,
            "Close": 51.00,
            "Adj Close": 51.00,
            "Volume": "-",
        },
    ]

    # Add enough history to satisfy the validator.
    valid_rows = [
        {
            "Date": f"{month:02d}-Jan-24",
            "Open": 50.00 + month,
            "High": 50.50 + month,
            "Low": 49.50 + month,
            "Close": 50.00 + month,
            "Adj Close": 50.00 + month,
            "Volume": "-",
        }
        for month in range(1, 25)
    ]

    valid_source = root / "TEST.csv"
    write_csv(valid_source, valid_rows)

    # ---------------------------------------------------------
    # 1. Valid CSV can be imported.
    # ---------------------------------------------------------

    result = manager.import_file(valid_source)

    assert result.imported
    assert not result.replaced
    assert result.destination == data_dir / "TEST.csv"
    assert result.validation.valid

    print("PASS: Valid fund CSV was imported.")

    # ---------------------------------------------------------
    # 2. Invalid CSV is rejected.
    # ---------------------------------------------------------

    invalid_source = root / "BAD.csv"

    invalid_rows = [
        {
            "Date": "not-a-date",
            "Adj Close": "not-a-price",
        }
        for _ in range(24)
    ]

    write_csv(invalid_source, invalid_rows)

    result = manager.import_file(invalid_source)

    assert not result.imported
    assert not result.validation.valid
    assert not (data_dir / "BAD.csv").exists()

    print("PASS: Invalid fund CSV was rejected.")

    # ---------------------------------------------------------
    # 3. Existing fund cannot be overwritten by default.
    # ---------------------------------------------------------

    try:
        manager.import_file(valid_source)
    except FileExistsError:
        pass
    else:
        raise AssertionError(
            "Existing fund was overwritten without replace=True."
        )

    print("PASS: Existing fund was protected from overwrite.")

    # ---------------------------------------------------------
    # 4. Existing fund can be safely replaced.
    # ---------------------------------------------------------

    replacement_rows = [
        {
            "Date": f"{month:02d}-Jan-24",
            "Open": 100.00 + month,
            "High": 100.50 + month,
            "Low": 99.50 + month,
            "Close": 100.00 + month,
            "Adj Close": 100.00 + month,
            "Volume": "-",
        }
        for month in range(1, 25)
    ]

    replacement_source = root / "TEST_REPLACEMENT.csv"
    write_csv(replacement_source, replacement_rows)

    # The filename determines the symbol, so use TEST.csv
    replacement_source = root / "TEST.csv"
    write_csv(replacement_source, replacement_rows)

    result = manager.import_file(
        replacement_source,
        replace=True,
    )

    assert result.imported
    assert result.replaced
    assert result.validation.valid

    installed = pd.read_csv(
        data_dir / "TEST.csv"
    )

    assert float(installed.iloc[0]["Adj Close"]) == 101.00

    print("PASS: Existing fund was safely replaced.")

    # ---------------------------------------------------------
    # 5. Removing an unused fund works.
    # ---------------------------------------------------------

    remove_result = manager.remove_fund("TEST")

    assert remove_result.removed
    assert not (data_dir / "TEST.csv").exists()

    print("PASS: Unused fund was removed.")

    # ---------------------------------------------------------
    # Re-import for portfolio protection test.
    # ---------------------------------------------------------

    manager.import_file(valid_source)

    # ---------------------------------------------------------
    # 6. Fund used by a portfolio cannot be removed.
    # ---------------------------------------------------------

    portfolio = {
        "name": "Test Portfolio",
        "holdings": [
            {
                "symbol": "TEST",
                "weight": 1.0,
            }
        ],
    }

    portfolio_path = (
        portfolio_dir / "TestPortfolio.json"
    )

    portfolio_path.write_text(
        json.dumps(portfolio),
        encoding="utf-8",
    )

    try:
        manager.remove_fund("TEST")
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Fund used by a portfolio was removed."
        )

    assert (data_dir / "TEST.csv").exists()

    print(
        "PASS: Fund used by a portfolio was protected."
    )

    # ---------------------------------------------------------
    # 7. Missing fund removal is rejected.
    # ---------------------------------------------------------

    try:
        manager.remove_fund("MISSING")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError(
            "Missing fund removal was not rejected."
        )

    print("PASS: Missing fund removal was rejected.")

    # ---------------------------------------------------------
    # 8. Entire library can be validated.
    # ---------------------------------------------------------

    results = manager.validate_all()

    assert len(results) == 1
    assert results[0].symbol == "TEST"
    assert results[0].valid

    print("PASS: Complete fund library validation succeeded.")


print("PASS: FundDataManager test suite completed.")
