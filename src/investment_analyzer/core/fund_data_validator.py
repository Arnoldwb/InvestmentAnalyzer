from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class ValidationResult:
    """
    Result of validating a fund CSV file.
    """

    path: Path
    symbol: str
    valid: bool = False
    row_count: int = 0
    usable_rows: int = 0
    distribution_rows: int = 0
    ignored_rows: int = 0
    first_date: pd.Timestamp | None = None
    last_date: pd.Timestamp | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.errors:
            return "ERROR"
        if self.warnings:
            return "WARNING"
        return "VALID"


class FundDataValidator:
    """
    Validate prospective Investment Analyzer CSV data files.

    Validation occurs before a file is copied into DATA_DIR.
    """

    REQUIRED_COLUMNS = {
        "Date",
        "Adj Close",
    }

    MINIMUM_USABLE_ROWS = 24
    MINIMUM_HISTORY_MONTHS = 24

    def _parse_dates(self, values):
        """
        Parse Investment Analyzer dates while allowing common
        alternative CSV date formats.
        """

        parsed = pd.to_datetime(
            values,
            format="%d-%b-%y",
            errors="coerce",
        )

        unresolved = parsed.isna() & values.notna()

        if unresolved.any():
            alternative = pd.to_datetime(
                values[unresolved],
                format="mixed",
                errors="coerce",
            )

            parsed.loc[unresolved] = alternative

        return parsed

    def validate(self, filename) -> ValidationResult:
        path = Path(filename)
        symbol = path.stem.strip().upper()

        result = ValidationResult(
            path=path,
            symbol=symbol,
        )

        if not path.exists():
            result.errors.append(
                f"File does not exist: {path}"
            )
            return result

        if not path.is_file():
            result.errors.append(
                f"Not a file: {path}"
            )
            return result

        if path.suffix.lower() != ".csv":
            result.errors.append(
                "File must have a .csv extension."
            )
            return result

        if not symbol:
            result.errors.append(
                "The CSV filename must contain an asset symbol."
            )
            return result

        try:
            data = pd.read_csv(path)
        except Exception as error:
            result.errors.append(
                f"Unable to read CSV file: {error}"
            )
            return result

        result.row_count = len(data)

        if data.empty:
            result.errors.append(
                "CSV file contains no data rows."
            )
            return result

        original_columns = list(data.columns)

        data.columns = [
            str(column).strip()
            for column in data.columns
        ]

        if original_columns != list(data.columns):
            result.warnings.append(
                "Column-name whitespace will be normalized."
            )

        missing_columns = sorted(
            self.REQUIRED_COLUMNS - set(data.columns)
        )

        if missing_columns:
            result.errors.append(
                "Missing required column(s): "
                + ", ".join(missing_columns)
            )
            return result

        parsed_dates = self._parse_dates(
            data["Date"]
        )

        adjusted_close = pd.to_numeric(
            data["Adj Close"],
            errors="coerce",
        )

        # Recognize distribution/event rows commonly found
        # in downloaded historical fund data.
        if "Open" in data.columns:
            open_text = (
                data["Open"]
                .fillna("")
                .astype(str)
                .str.lower()
            )

            distribution_mask = (
                parsed_dates.notna()
                & adjusted_close.isna()
                & open_text.str.contains(
                    "distribution",
                    regex=False,
                )
            )
        else:
            distribution_mask = pd.Series(
                False,
                index=data.index,
            )

        result.distribution_rows = int(
            distribution_mask.sum()
        )

        if result.distribution_rows:
            result.warnings.append(
                f"{result.distribution_rows:,} "
                "distribution/event row(s) will be ignored."
            )

        # Rows with neither a usable date nor a usable price
        # are treated as blank/footer/junk material.
        junk_mask = (
            parsed_dates.isna()
            & adjusted_close.isna()
        )

        result.ignored_rows = int(
            junk_mask.sum()
        )

        if result.ignored_rows:
            result.warnings.append(
                f"{result.ignored_rows:,} blank or non-data "
                "row(s) will be ignored."
            )

        recognized_nonprice = (
            distribution_mask
            | junk_mask
        )

        bad_date_mask = (
            parsed_dates.isna()
            & ~recognized_nonprice
        )

        bad_price_mask = (
            adjusted_close.isna()
            & ~recognized_nonprice
        )

        bad_date_count = int(
            bad_date_mask.sum()
        )

        bad_price_count = int(
            bad_price_mask.sum()
        )

        if bad_date_count:
            result.errors.append(
                f"{bad_date_count:,} row(s) contain "
                "an invalid or missing Date."
            )

        if bad_price_count:
            result.errors.append(
                f"{bad_price_count:,} row(s) contain "
                "an invalid or missing Adj Close value."
            )

        valid_mask = (
            parsed_dates.notna()
            & adjusted_close.notna()
        )

        usable_dates = parsed_dates[valid_mask]
        usable_prices = adjusted_close[valid_mask]

        result.usable_rows = int(
            valid_mask.sum()
        )

        if result.usable_rows:
            result.first_date = usable_dates.min()
            result.last_date = usable_dates.max()

        nonpositive_count = int(
            (usable_prices <= 0).sum()
        )

        if nonpositive_count:
            result.errors.append(
                f"{nonpositive_count:,} row(s) contain "
                "a zero or negative Adj Close value."
            )

        duplicate_count = int(
            usable_dates.duplicated().sum()
        )

        if duplicate_count:
            result.errors.append(
                f"{duplicate_count:,} duplicate Date "
                "row(s) were found."
            )

        if (
            result.usable_rows
            < self.MINIMUM_USABLE_ROWS
        ):
            result.errors.append(
                "Insufficient usable history: "
                f"{result.usable_rows:,} row(s). "
                f"At least {self.MINIMUM_USABLE_ROWS} "
                "are required."
            )

        if (
            result.first_date is not None
            and result.last_date is not None
        ):
            history_days = (
                result.last_date - result.first_date
            ).days

            approximate_months = history_days / 30.4375

            if approximate_months < self.MINIMUM_HISTORY_MONTHS:
                result.errors.append(
                    "Insufficient historical coverage: "
                    f"approximately {approximate_months:.1f} month(s). "
                    f"At least {self.MINIMUM_HISTORY_MONTHS} "
                    "months of history are required."
                )

        if usable_dates.is_monotonic_decreasing:
            result.warnings.append(
                "Dates are newest-first and will be "
                "sorted automatically."
            )
        elif not usable_dates.is_monotonic_increasing:
            result.warnings.append(
                "Dates are not in chronological order "
                "and will be sorted automatically."
            )

        result.valid = not result.errors

        return result
